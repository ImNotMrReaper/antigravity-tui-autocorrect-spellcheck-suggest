#!/usr/bin/env python3
"""
tui_autocorrect.py: Advanced Inline Predictive Autocomplete, Grey Ghost-Text Suggestive Text,
Levenshtein Spellchecker, and PTY Interactive Supervisor for Antigravity Terminal Sessions (AGY TUI).

Integrates:
- Real-time grey ghost-text completion ahead of the cursor (ble.sh parity)
- Tab and Right Arrow completion acceptance
- Real-time typo autocorrection & spellchecking (on Space/Enter/punctuation)
- Persistent user vocabulary synchronization (~/.config/reaper-notes/user_vocabulary.db)
- Native PTY terminal pass-through with window resize (SIGWINCH) and zero-latency lookups (<1ms)
"""

import os
import sys
import time
import signal
import select
import fcntl
import termios
import tty
import pty
import sqlite3
from pathlib import Path
from typing import List, Optional, Tuple, Dict, Set

VOCAB_DB_PATH = Path.home() / ".config" / "reaper-notes" / "user_vocabulary.db"

# Exhaustive dictionary of system, developer, Linux, and prompt vocabulary
COMMON_KEYWORDS = [
    # System, Antigravity & AI
    "antigravity", "agy", "senpai", "reaper", "cortex", "hermes", "subagent",
    "autocomplete", "autocorrect", "suggestive", "terminal", "session", "prompt",
    "generator", "assistant", "whisper", "vulkan", "biometric", "fingerprint",
    "howdy", "fprintd", "joycon", "bluetooth", "obsidian", "terminator",
    # Dev & Python
    "python", "python3", "import", "from", "return", "def", "class", "async",
    "await", "lambda", "except", "finally", "raise", "assert", "global",
    "yield", "continue", "break", "print", "range", "enumerate", "isinstance",
    "package", "install", "upgrade", "uninstall", "module", "virtualenv",
    # Linux & Bash
    "sudo", "systemctl", "journalctl", "chmod", "chown", "mkdir", "touch",
    "export", "source", "echo", "grep", "find", "curl", "wget", "which",
    "status", "commit", "checkout", "branch", "clone", "pull", "push",
    "desktop", "window", "display", "monitor", "restore", "extension",
    "checker", "spellcheck", "spellchecker", "dictionary", "vocabulary",
    # English Common Vocabulary
    "about", "after", "again", "almost", "already", "always", "another",
    "answer", "appear", "around", "before", "beginning", "behavior",
    "behind", "believe", "between", "bottom", "change", "check", "choose",
    "clean", "clear", "complete", "condition", "config", "configuration",
    "connect", "connection", "control", "current", "database", "default",
    "define", "delete", "detail", "device", "different", "direct",
    "directory", "discover", "document", "element", "enable", "engine",
    "enough", "ensure", "environment", "error", "example", "execute",
    "execution", "existing", "expect", "explain", "extend", "extension",
    "feature", "filter", "finish", "follow", "forward", "framework",
    "frequency", "function", "future", "general", "generate", "global",
    "hardware", "header", "history", "identify", "implement", "important",
    "include", "initial", "initialize", "insert", "inspect", "install",
    "integrate", "interface", "internal", "keyboard", "kernel", "launch",
    "launcher", "layout", "length", "library", "license", "lightweight",
    "linux", "listen", "location", "lookup", "machine", "manage", "manager",
    "manual", "match", "matrix", "memory", "message", "method", "minute",
    "model", "modify", "multiple", "native", "necessary", "network",
    "nothing", "notice", "number", "object", "operation", "optimize",
    "option", "output", "parallel", "pattern", "perform", "permission",
    "physical", "pipeline", "platform", "plugin", "policy", "position",
    "predict", "predictive", "preference", "previous", "priority", "process",
    "profile", "program", "project", "protocol", "provide", "random",
    "receive", "record", "recorder", "reference", "register", "release",
    "reload", "remove", "replace", "report", "request", "require", "reset",
    "resolve", "resource", "response", "restore", "result", "running",
    "sample", "scaffold", "schedule", "screen", "script", "search",
    "section", "secure", "security", "select", "selection", "sensor",
    "separate", "sequence", "server", "service", "shortcut", "simulate",
    "software", "solution", "source", "standard", "start", "state",
    "storage", "string", "structure", "submit", "subsystem", "succeed",
    "success", "suggest", "suggestion", "support", "switch", "system",
    "table", "tandem", "target", "task", "testing", "theme", "threshold",
    "timeout", "timestamp", "toggle", "tracking", "trajectory", "trigger",
    "ubuntu", "understand", "unified", "universal", "unlock", "update",
    "useful", "validate", "value", "variable", "version", "voice", "volume",
    "wait", "warning", "window", "wrapper"
]

# Exact typo replacements map (instant O(1) resolution)
COMMON_CORRECTIONS = {
    # Antigravity & User Prompt Typos
    "autocompleat": "autocomplete",
    "autocomplet": "autocomplete",
    "autocompleting": "autocomplete",
    "seuestive": "suggestive",
    "sugestive": "suggestive",
    "sugest": "suggest",
    "termail": "terminal",
    "terminl": "terminal",
    "teminal": "terminal",
    "cheacher": "checker",
    "cheacker": "checker",
    "spellchecker": "spellchecker",
    "antigravty": "antigravity",
    "anti-gravity": "antigravity",
    "suod": "sudo",
    "tehn": "then",
    "taht": "that",
    "recieve": "receive",
    "seperat": "separate",
    "definately": "definitely",
    "reusme": "resume",
    "improt": "import",
    "seledt": "select",
    "valut": "vault",
    "signiture": "signature",
    "importent": "important",
    "pacakge": "package",
    "packge": "package",
    "whcih": "which",
    "lfet": "left",
    "pyhton": "python",
    "instal": "install",
    "instalation": "installation",
    "managment": "management",
    "enviroment": "environment",
    "repositary": "repository",
    "respository": "repository",
    "commmit": "commit",
    "stauts": "status",
    "functon": "function",
    "variabel": "variable",
    "paramater": "parameter",
    "messsage": "message",
    "reponse": "response",
    "restor": "restore",
}


class TrieNode:
    __slots__ = ("children", "is_word", "frequency")

    def __init__(self):
        self.children: Dict[str, "TrieNode"] = {}
        self.is_word: bool = False
        self.frequency: int = 0


class AutocompleteTrie:
    """Sub-millisecond prefix Trie matcher with SQLite frequency scoring."""

    def __init__(self):
        self.root = TrieNode()
        self.loaded = False

    def insert(self, word: str, freq: int = 1):
        clean = word.strip().lower()
        if len(clean) < 2:
            return
        node = self.root
        for char in clean:
            if char not in node.children:
                node.children[char] = TrieNode()
            node = node.children[char]
        node.is_word = True
        node.frequency = max(node.frequency, freq)

    def load_all(self):
        if self.loaded:
            return
        # 1. Load built-in vocabulary keywords
        for kw in COMMON_KEYWORDS:
            self.insert(kw, freq=5)

        # 2. Load user persistent vocabulary
        if VOCAB_DB_PATH.exists():
            try:
                conn = sqlite3.connect(str(VOCAB_DB_PATH), timeout=2.0)
                with conn:
                    cur = conn.execute("SELECT word, frequency FROM word_frequencies;")
                    for w, f in cur.fetchall():
                        self.insert(w, f)
            except Exception:
                pass
        self.loaded = True

    def get_best_completion(self, prefix: str) -> str:
        if not prefix or len(prefix) < 2:
            return ""
        node = self.root
        p_low = prefix.lower()
        for char in p_low:
            if char not in node.children:
                return ""
            node = node.children[char]

        # Find highest frequency completion
        best_word = ""
        best_freq = -1
        stack = [(node, p_low)]
        while stack:
            curr, path = stack.pop()
            if curr.is_word and curr.frequency > best_freq and len(path) > len(prefix):
                best_freq = curr.frequency
                best_word = path
            for ch, child in curr.children.items():
                stack.append((child, path + ch))
        return best_word


def get_db_connection() -> Optional[sqlite3.Connection]:
    if not VOCAB_DB_PATH.exists():
        return None
    try:
        return sqlite3.connect(str(VOCAB_DB_PATH), timeout=3.0)
    except Exception:
        return None


def record_user_word(word: str, count: int = 1):
    """Records or increments a word in the persistent frequency database."""
    clean = word.strip().lower()
    if len(clean) < 2 or not clean[0].isalpha():
        return
    VOCAB_DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    try:
        conn = sqlite3.connect(str(VOCAB_DB_PATH), timeout=3.0)
        with conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS word_frequencies (
                    word TEXT PRIMARY KEY,
                    frequency INTEGER NOT NULL DEFAULT 1,
                    last_used REAL NOT NULL
                );
            """)
            conn.execute("""
                INSERT INTO word_frequencies (word, frequency, last_used)
                VALUES (?, ?, ?)
                ON CONFLICT(word) DO UPDATE SET
                    frequency = frequency + excluded.frequency,
                    last_used = excluded.last_used;
            """, (clean, count, time.time()))
    except Exception:
        pass


def levenshtein(s1: str, s2: str) -> int:
    if len(s1) < len(s2):
        return levenshtein(s2, s1)
    if len(s2) == 0:
        return len(s1)
    previous_row = range(len(s2) + 1)
    for i, c1 in enumerate(s1):
        current_row = [i + 1]
        for j, c2 in enumerate(s2):
            insertions = previous_row[j + 1] + 1
            deletions = current_row[j] + 1
            substitutions = previous_row[j] + (c1 != c2)
            current_row.append(min(insertions, deletions, substitutions))
        previous_row = current_row
    return previous_row[-1]


def correct_word(word: str) -> str:
    """Spellchecks and autocorrects a single word with case preservation."""
    clean = word.strip().lower()
    if not clean:
        return word

    # 1. Exact match in typo dictionary
    if clean in COMMON_CORRECTIONS:
        corr = COMMON_CORRECTIONS[clean]
        if word.isupper():
            return corr.upper()
        if word[0].isupper():
            return corr.capitalize()
        return corr

    # 2. If already valid keyword, preserve it
    if clean in COMMON_KEYWORDS:
        return word

    # 3. Fuzzy Levenshtein match for words >= 4 chars
    if len(clean) >= 4:
        for candidate in COMMON_KEYWORDS:
            if abs(len(candidate) - len(clean)) <= 2 and candidate[0] == clean[0]:
                max_d = 2 if len(clean) >= 6 else 1
                if levenshtein(clean, candidate) <= max_d:
                    if word.isupper():
                        return candidate.upper()
                    if word[0].isupper():
                        return candidate.capitalize()
                    return candidate

    return word


class AgyPtySupervisor:
    """
    PTY Interactive Supervisor for Antigravity sessions.
    Proxies terminal I/O, renders inline grey ghost text ahead of the cursor,
    intercepts Tab and Right-Arrow for instant completion, and corrects typos
    on Space/Enter/punctuation in real time.
    """

    def __init__(self, command: List[str]):
        self.command = command
        self.trie = AutocompleteTrie()
        self.trie.load_all()
        self.active_ghost = ""
        self.current_word = ""
        self.in_slash = False
        self.master_fd = None
        self.child_pid = None
        self.orig_termios = None

    def _clear_ghost_screen(self):
        if self.active_ghost:
            spaces = " " * len(self.active_ghost)
            sys.stdout.buffer.write(f"\0337{spaces}\0338".encode("utf-8"))
            sys.stdout.buffer.flush()
            self.active_ghost = ""

    def _render_ghost_screen(self, ghost: str):
        if ghost != self.active_ghost:
            self._clear_ghost_screen()
            self.active_ghost = ghost
            sys.stdout.buffer.write(f"\0337\033[90m{ghost}\033[0m\0338".encode("utf-8"))
            sys.stdout.buffer.flush()

    def run(self):
        if not sys.stdin.isatty() or not sys.stdout.isatty():
            os.execvp(self.command[0], self.command)
            return

        self.orig_termios = termios.tcgetattr(sys.stdin.fileno())
        self.master_fd, slave_fd = pty.openpty()

        # Copy terminal window size
        try:
            winsize = fcntl.ioctl(sys.stdin.fileno(), termios.TIOCGWINSZ, b"\x00" * 8)
            fcntl.ioctl(self.master_fd, termios.TIOCSWINSZ, winsize)
        except Exception:
            pass

        def sigwinch_handler(signum, frame):
            try:
                ws = fcntl.ioctl(sys.stdin.fileno(), termios.TIOCGWINSZ, b"\x00" * 8)
                fcntl.ioctl(self.master_fd, termios.TIOCSWINSZ, ws)
            except Exception:
                pass

        signal.signal(signal.SIGWINCH, sigwinch_handler)

        self.child_pid = os.fork()
        if self.child_pid == 0:
            # Child process: runs agy under synthetic PTY
            os.close(self.master_fd)
            os.setsid()
            os.dup2(slave_fd, 0)
            os.dup2(slave_fd, 1)
            os.dup2(slave_fd, 2)
            os.close(slave_fd)
            try:
                os.execvp(self.command[0], self.command)
            except Exception as e:
                sys.stderr.write(f"Failed to execute {self.command[0]}: {e}\n")
                sys.exit(1)

        # Parent process: supervisor
        os.close(slave_fd)
        tty.setraw(sys.stdin.fileno())

        try:
            self._event_loop()
        finally:
            self._cleanup()

    def _cleanup(self):
        self._clear_ghost_screen()
        if self.orig_termios:
            try:
                termios.tcsetattr(sys.stdin.fileno(), termios.TCSADRAIN, self.orig_termios)
            except Exception:
                pass
        if self.master_fd is not None:
            try:
                os.close(self.master_fd)
            except Exception:
                pass

    def _event_loop(self):
        pending_ghost_render = False

        while True:
            try:
                rlist, _, _ = select.select([sys.stdin.fileno(), self.master_fd], [], [])
            except (InterruptedError, select.error):
                continue

            # 1. Output from child (agy) to screen
            if self.master_fd in rlist:
                try:
                    data = os.read(self.master_fd, 4096)
                except OSError:
                    # Child process exited
                    break
                if not data:
                    break
                sys.stdout.buffer.write(data)
                sys.stdout.buffer.flush()

                if pending_ghost_render:
                    if self.current_word and len(self.current_word) >= 2 and not self.in_slash:
                        best = self.trie.get_best_completion(self.current_word)
                        if best and len(best) > len(self.current_word):
                            ghost = best[len(self.current_word):]
                            self._render_ghost_screen(ghost)
                        else:
                            self._clear_ghost_screen()
                    else:
                        self._clear_ghost_screen()
                    pending_ghost_render = False

            # 2. Input from user keyboard
            if sys.stdin.fileno() in rlist:
                try:
                    chunk = os.read(sys.stdin.fileno(), 1024)
                except OSError:
                    break
                if not chunk:
                    break

                # Handle single-byte input
                if len(chunk) == 1:
                    b = chunk[0]

                    # Ctrl+C (0x03) or Ctrl+D (0x04)
                    if b in (0x03, 0x04):
                        self._clear_ghost_screen()
                        self.current_word = ""
                        self.in_slash = False
                        os.write(self.master_fd, chunk)
                        continue

                    # Tab (0x09) -> Accept ghost completion
                    if b == 0x09:
                        if self.active_ghost:
                            ghost_text = self.active_ghost
                            self._clear_ghost_screen()
                            os.write(self.master_fd, ghost_text.encode("utf-8"))
                            self.current_word += ghost_text
                            continue
                        else:
                            self._clear_ghost_screen()
                            os.write(self.master_fd, chunk)
                            continue

                    # Backspace (0x7F or 0x08)
                    if b in (0x7F, 0x08):
                        self._clear_ghost_screen()
                        os.write(self.master_fd, chunk)
                        if self.current_word:
                            self.current_word = self.current_word[:-1]
                            if len(self.current_word) >= 2 and not self.in_slash:
                                pending_ghost_render = True
                        continue

                    # Delimiter: Space, Enter, or Punctuation
                    if b in (0x20, 0x0D, 0x0A) or chr(b) in ",.!?:;()[]{}'\"":
                        self._clear_ghost_screen()
                        if self.current_word and not self.in_slash:
                            corr = correct_word(self.current_word)
                            if corr != self.current_word:
                                # Erase typo from agy's buffer
                                os.write(self.master_fd, b"\x7f" * len(self.current_word))
                                # Send corrected word
                                os.write(self.master_fd, corr.encode("utf-8"))
                                record_user_word(corr)
                            else:
                                if len(self.current_word) >= 2 and self.current_word[0].isalpha():
                                    record_user_word(self.current_word)
                        self.current_word = ""
                        self.in_slash = False
                        os.write(self.master_fd, chunk)
                        continue

                    # Slash command trigger (/)
                    if b == ord("/"):
                        if self.current_word == "":
                            self.in_slash = True
                        self._clear_ghost_screen()
                        self.current_word = ""
                        os.write(self.master_fd, chunk)
                        continue

                    # Word characters: letters, digits, underscore, dash
                    char = chr(b)
                    if char.isalnum() or char in ("_", "-"):
                        self._clear_ghost_screen()
                        os.write(self.master_fd, chunk)
                        if not self.in_slash:
                            self.current_word += char
                            if len(self.current_word) >= 2:
                                pending_ghost_render = True
                        continue

                    # Other single characters
                    self._clear_ghost_screen()
                    self.current_word = ""
                    self.in_slash = False
                    os.write(self.master_fd, chunk)
                    continue

                # Handle multi-byte sequences (escape sequences, arrows, paste)
                if len(chunk) > 1:
                    # Right Arrow (\x1b[C or \x1bOC) -> Accept ghost completion
                    if chunk in (b"\x1b[C", b"\x1bOC"):
                        if self.active_ghost:
                            ghost_text = self.active_ghost
                            self._clear_ghost_screen()
                            os.write(self.master_fd, ghost_text.encode("utf-8"))
                            self.current_word += ghost_text
                            continue
                        else:
                            self._clear_ghost_screen()
                            os.write(self.master_fd, chunk)
                            continue

                    # Up/Down/Left arrows, Home, End
                    if chunk in (b"\x1b[A", b"\x1b[B", b"\x1b[D", b"\x1bOA", b"\x1bOB", b"\x1bOD", b"\x1b[H", b"\x1b[F"):
                        self._clear_ghost_screen()
                        self.current_word = ""
                        self.in_slash = False
                        os.write(self.master_fd, chunk)
                        continue

                    # Multi-character paste
                    self._clear_ghost_screen()
                    self.current_word = ""
                    self.in_slash = False
                    os.write(self.master_fd, chunk)
                    continue

        # Wait for child process termination
        if self.child_pid:
            try:
                _, status = os.waitpid(self.child_pid, 0)
                sys.exit(os.WEXITSTATUS(status) if os.WIFEXITED(status) else 1)
            except Exception:
                sys.exit(0)


def run_pty_supervisor(cmd: List[str]):
    supervisor = AgyPtySupervisor(cmd)
    supervisor.run()


if __name__ == "__main__":
    args = sys.argv[1:]
    if not args:
        print("Usage: tui_autocorrect.py [--wrap <cmd...>] [--suggest <prefix>] [--record <word>] <word1> [word2...]")
        sys.exit(0)

    if args[0] == "--wrap" and len(args) > 1:
        run_pty_supervisor(args[1:])
    elif args[0] == "--suggest" and len(args) > 1:
        trie = AutocompleteTrie()
        trie.load_all()
        best = trie.get_best_completion(args[1])
        if best:
            print(f"Best: {best} (Ghost: {best[len(args[1]):]})")
        else:
            print("No suggestion.")
    elif args[0] == "--record" and len(args) > 1:
        for w in args[1:]:
            record_user_word(w)
        print("Recorded.")
    else:
        corrected = [correct_word(w) for w in args]
        print(" ".join(corrected))
