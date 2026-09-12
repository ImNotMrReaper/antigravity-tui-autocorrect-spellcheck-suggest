# Antigravity TUI Autocomplete & Suggestive Text Engine

Fast inline predictive autosuggestion, Levenshtein distance spellchecking/autocorrect, and slash command auto-expansion for Antigravity interactive CLI and terminal pair-programming sessions.

## Features
- **Inline Ghost-Text Prediction:** Evaluates typed sequences against technical dictionaries, codebase symbols, and command templates.
- **Fuzzy Levenshtein Autocorrect:** Corrects frequent slips (`tehn` -> `then`, `antigravty` -> `antigravity`, `autocompleate` -> `autocomplete`, `suod` -> `sudo`, `reusme` -> `resume`).
- **Slash Command Expansion:** Instant completion for Antigravity slash directives (`/link`, `/voice`, `/senpai`, `/inbox`, `/goal`, `/plan`, `/grill-me`, `/boost`).
- **Sub-5ms Execution:** Pure Python zero-dependency engine suitable for interactive terminal environments.

## Installation
Symlink into Antigravity plugins directory:
```bash
ln -s ~/PycharmProjects/tui-autocomplete ~/.gemini/config/plugins/tui-autocomplete
```

## Testing CLI Autocorrect
```bash
python3 scripts/tui_autocorrect.py tehn antigravty autocompleate suod reusme
# Output: then antigravity autocomplete sudo resume
```

## License
MIT
