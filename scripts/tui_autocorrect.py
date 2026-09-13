#!/usr/bin/env python3
"""
tui_autocorrect.py: Fast Levenshtein distance spellchecker, suggestive text,
and user frequency database engine for Antigravity terminal sessions and prompt typing.
"""

import sys
import time
import sqlite3
from pathlib import Path
from typing import List, Optional, Tuple, Dict

VOCAB_DB_PATH = Path.home() / ".config" / "reaper-notes" / "user_vocabulary.db"

DICTIONARY = {
    # System & Dev
    "antigravity": ["antigravity", "agy", "assistant"],
    "autocomplete": ["autocomplete", "autocompletion"],
    "autocorrect": ["autocorrect"],
    "keyboard": ["keyboard"],
    "terminal": ["terminal"],
    "obsidian": ["obsidian"],
    "whisper": ["whisper"],
    "vulkan": ["vulkan"],
    "biometric": ["biometric"],
    "fingerprint": ["fingerprint"],
    "bluetooth": ["bluetooth"],
    "joycon": ["joycon"],
    "linux": ["linux"],
    "ubuntu": ["ubuntu"],
    "reaper": ["reaper"],
    # Commands & Common Words
    "then": ["then"],
    "sudo": ["sudo"],
    "python": ["python"],
    "status": ["status"],
    "commit": ["commit"],
    "install": ["install"],
    "resume": ["resume"],
    "finish": ["finish"],
    "generate": ["generate"],
    "package": ["package"],
}

COMMON_CORRECTIONS = {
    "tehn": "then",
    "taht": "that",
    "recieve": "receive",
    "seperat": "separate",
    "definately": "definitely",
    "antigravty": "antigravity",
    "autocompleate": "autocomplete",
    "suod": "sudo",
    "reusme": "resume",
    "improt": "import",
    "seledt": "select",
    "valut": "vault",
    "signiture": "signature",
    "importent": "important",
    "seuestive": "suggestive",
    "termail": "terminal",
}



def get_db_connection() -> Optional[sqlite3.Connection]:
    if not VOCAB_DB_PATH.exists():
        return None
    try:
        conn = sqlite3.connect(str(VOCAB_DB_PATH), timeout=3.0)
        return conn
    except Exception:
        return None


def get_frequent_suggestions(prefix: str, limit: int = 5) -> List[Tuple[str, int]]:
    """Returns top matches from user's persistent frequency database."""
    conn = get_db_connection()
    if not conn:
        # Fallback to in-memory dictionary
        matches = [w for w in DICTIONARY if w.startswith(prefix.lower())]
        return [(w, 1) for w in matches[:limit]]

    p_low = prefix.strip().lower()
    try:
        with conn:
            cursor = conn.execute("""
                SELECT word, frequency FROM word_frequencies
                WHERE word LIKE ? AND word != ?
                ORDER BY frequency DESC, last_used DESC, length(word) ASC
                LIMIT ?;
            """, (f"{p_low}%", p_low, limit))
            res = cursor.fetchall()
            if res:
                return res
    except Exception:
        pass

    # Fallback to builtins
    matches = [w for w in DICTIONARY if w.startswith(p_low)]
    return [(w, 1) for w in matches[:limit]]


def record_user_word(word: str, count: int = 1):
    """Records or increments a word in the persistent frequency database."""
    clean = word.strip().lower()
    if len(clean) < 2 or not clean[0].isalpha():
        return
    VOCAB_DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    try:
        conn = sqlite3.connect(str(VOCAB_DB_PATH), timeout=5.0)
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
    lower = word.lower()
    if lower in COMMON_CORRECTIONS:
        return COMMON_CORRECTIONS[lower]

    # Check top frequency candidates first
    conn = get_db_connection()
    candidates = list(DICTIONARY.keys())
    if conn:
        try:
            with conn:
                cursor = conn.execute("SELECT word FROM word_frequencies ORDER BY frequency DESC LIMIT 200;")
                candidates = [row[0] for row in cursor.fetchall()] + candidates
        except Exception:
            pass

    best_match = word
    min_dist = 3
    for candidate in candidates:
        dist = levenshtein(lower, candidate)
        if dist < min_dist:
            min_dist = dist
            best_match = candidate

    return best_match if min_dist <= 2 else word


if __name__ == "__main__":
    args = sys.argv[1:]
    if not args:
        print("Usage: tui_autocorrect.py [--suggest <prefix>] [--record <word>] <word1> [word2...]")
        sys.exit(0)

    if args[0] == "--suggest" and len(args) > 1:
        prefix = args[1]
        results = get_frequent_suggestions(prefix, limit=5)
        for w, freq in results:
            print(f"{w} ({freq})")
    elif args[0] == "--record" and len(args) > 1:
        for w in args[1:]:
            record_user_word(w)
        print("Recorded.")
    else:
        corrected = [correct_word(w) for w in args]
        print(" ".join(corrected))
