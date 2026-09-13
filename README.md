# Antigravity TUI Autocomplete & Suggestive Text Engine

Fast inline predictive autosuggestion, Levenshtein distance spellchecking/autocorrect, and slash command auto-expansion for Antigravity interactive CLI and terminal pair-programming sessions.

## Features
- **Inline Ghost-Text Prediction:** Evaluates typed sequences against technical dictionaries, codebase symbols, and command templates.
- **Fuzzy Levenshtein Autocorrect:** Corrects frequent slips (`tehn` -> `then`, `antigravty` -> `antigravity`, `autocompleate` -> `autocomplete`, `suod` -> `sudo`, `reusme` -> `resume`).
- **Slash Command Expansion:** Instant completion for Antigravity slash directives (`/link`, `/voice`, `/senpai`, `/inbox`, `/goal`, `/plan`, `/grill-me`, `/boost`).
- **Sub-5ms Execution:** Pure Python zero-dependency engine suitable for interactive terminal environments.

## 🚀 Quick Start (1-Line Installation)

Install the Antigravity plugin, agent skill, and terminal CLI tool with a single command:

```bash
curl -fsSL https://raw.githubusercontent.com/ImNotMrReaper/tui-autocomplete/main/install.sh | bash
```

### Manual Installation
```bash
git clone https://github.com/ImNotMrReaper/tui-autocomplete.git
cd tui-autocomplete
./install.sh
```

## Testing CLI Autocorrect
```bash
python3 scripts/tui_autocorrect.py tehn antigravty autocompleate suod reusme
# Output: then antigravity autocomplete sudo resume
```

## License
MIT
