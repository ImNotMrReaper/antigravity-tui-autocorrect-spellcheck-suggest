# agy-suggest: Antigravity TUI Autocorrect, Spell Checker & Suggestive Text Engine

Fast inline predictive autosuggestion, grey ghost-text completion (`ble.sh` parity), Levenshtein distance spellchecking/autocorrect, and slash command auto-expansion for Antigravity interactive CLI and terminal pair-programming sessions.

## Features
- **Inline Grey Ghost-Text Prediction (ble.sh Parity):** Evaluates typed sequences in real time and renders low-contrast dimmed ghost text ahead of the cursor.
- **Tab & Right Arrow Completion:** Instant single-keystroke acceptance of suggested text directly into the active prompt buffer.
- **Real-Time Typo Spellchecker:** Automatically detects and replaces common spelling errors (`autocompleat` -> `autocomplete`, `seuestive` -> `suggestive`, `termail` -> `terminal`, `cheacher` -> `checker`, `tehn` -> `then`, `suod` -> `sudo`) on Space, Enter, or punctuation.
- **Interactive PTY Supervisor (`agy` / `antigravity`):** Transparent zero-latency PTY wrapper intercepting keystrokes and handling terminal window resizing (`SIGWINCH`), Ctrl+C interrupts, and clipboard pastes smoothly.
- **Persistent Vocabulary Synchronization:** Shared SQLite database (`~/.config/reaper-notes/user_vocabulary.db`) tracks frequency and recency across `reaper-notes`, terminal commands, and Antigravity TUI sessions.
- **Slash Command Expansion:** Instant completion for Antigravity slash directives (`/link`, `/voice`, `/senpai`, `/inbox`, `/goal`, `/plan`, `/grill-me`, `/boost`).
- **Sub-1ms Execution:** Pure Python zero-dependency engine suitable for interactive terminal environments.

## 🚀 Quick Start (1-Line Installation)

Install the Antigravity plugin, agent skill, terminal CLI tool, and AGY supervisor with a single command:

```bash
curl -fsSL https://raw.githubusercontent.com/ImNotMrReaper/agy-suggest/main/install.sh | bash
```

### Manual Installation
```bash
git clone https://github.com/ImNotMrReaper/agy-suggest.git
cd agy-suggest
./install.sh
```

## Interactive AGY TUI Usage
Launch Antigravity CLI directly or resume your session with full inline autocomplete:
```bash
agy -c
# Or via full alias:
antigravity -c
```
- Type any word stem (e.g. `autocom` or `antigrav`) to see grey ghost text ahead of the cursor.
- Press <kbd>Tab</kbd> or <kbd>→</kbd> to accept the suggestion.
- Type any typo (e.g. `autocompleat`, `termail`, `cheacher`) and hit <kbd>Space</kbd> or <kbd>Enter</kbd> to watch it instantly autocorrect!

## Testing CLI Autocorrect
```bash
tui-autocorrect autocompleat seuestive termail cheacher tehn suod reusme
# Output: autocomplete suggestive terminal checker then sudo resume
```

## License
MIT
