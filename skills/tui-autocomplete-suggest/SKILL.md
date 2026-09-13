---
name: tui-autocomplete-suggest
description: >-
  Architectural specification and runbook for Antigravity TUI predictive autosuggestion,
  inline ghost-text autocompletion, slash command quick-templates, and fuzzy Levenshtein
  spellchecking/autocorrection across terminal sessions and text editor interfaces.
---

# Antigravity TUI Autocorrect, Spell Checker & Suggestive Text Engine

## 1. Overview
This skill provides bidirectional typing assistance, fuzzy Levenshtein spellchecking, grey ghost-text suggestive text, and inline predictive completion for Antigravity interactive terminal sessions and pair-programming workflows. It prevents typo drops, accelerates slash command execution, and provides automatic dictionary correction for technical vocabulary.

---

## 2. Core Features & Capabilities

1. **Prefix Ghost-Text Prediction:**
   - Evaluates input character sequences against command dictionaries, recent workspace symbols, and active files.
   - Renders low-contrast inline ghost text (dimmed/secondary palette) ahead of the cursor.
   - Accepts completion via <kbd>Tab</kbd> or <kbd>→</kbd> (Right Arrow).
   - Emulates Bash Line Editor (`ble.sh`) interactive suggestion physics:
     * Single-keystroke lookahead.
     * History-based recency weighting.
     * Ghost-text preview rendering.

2. **Fuzzy Levenshtein Autocorrection:**
   - Corrects common inverted or dropped character typos (distance $\le 2$):
     - `tehn` $\to$ `then`
     - `antigravty` $\to$ `antigravity`
     - `autocompleate` $\to$ `autocomplete`
     - `seuestive` $\to$ `suggestive`
     - `termail` $\to$ `terminal`
     - `suod` $\to$ `sudo`
     - `seledt` $\to$ `select`
     - `improt` $\to$ `import`

3. **Slash Command & Directive Expansion:**
   - Quick-expands `/link`, `/senpai`, `/inbox`, `/voice`, `/goal`, `/plan`, `/grill-me`, `/boost`, `/learn`, `/deepresearch` with parameter templates.

4. **Codebase Symbol Harvesting:**
   - Periodically caches high-frequency identifier tokens from current workspace git commits and active document buffers to prioritize local project nomenclature.


---

## 3. Configuration & Paths

- **Plugin Home:** `~/.gemini/config/plugins/tui-autocomplete/`
- **Plugin Manifest:** `~/.gemini/config/plugins/tui-autocomplete/plugin.json`
- **Dictionary & Engine:** `~/.gemini/config/plugins/tui-autocomplete/scripts/tui_autocorrect.py`
- **Editor Integration:** `reaper-notes` (`src/reaper_notes/autocomplete.py`)

---

## 4. Operational Guidelines

- Always favor high-frequency developer terminology and slash command formats.
- Suppress suggestions during fast continuous typing or shell pipe sequences.
- Keep completion lookup under 5 milliseconds to prevent keystroke lag.
