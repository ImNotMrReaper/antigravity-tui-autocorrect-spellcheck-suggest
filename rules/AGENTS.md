# Antigravity Fuzzy Autocorrect & Intent Interpretation Rule

1. **Typo Tolerance & Automatic Spellcheck:**
   - When the user types prompts with typos, missing letters, inverted characters (e.g. `tehn`, `reusme`, `lfet`, `suod`, `whcih`), silently autocorrect them to the intended words using Levenshtein minimum distance.
   - Never ask for clarification on obvious typos; resolve them automatically and proceed.

2. **Predictive Shorthand & Intent Expansion:**
   - Expand shorthand abbreviations into complete operations.
   - If the user provides a brief or fragmented instruction, infer the complete pair-programming objective based on recent session context and execute thoroughly.

3. **Terminal-Grade Auto-Suggestive Text (ble.sh Parity):**
   - Emulate interactive terminal line-editor behavior (like `ble.sh` in the user's `.bashrc`) inside Antigravity TUI sessions:
     - **Ghost-Text Style Previews:** When the user enters partial commands, slash shortcuts, or brief stems, proactively provide completions formatted as dimmed inline suggestions or compact bulleted completion templates.
     - **Slash Command Rapid Expansion:** Immediately recognize and expand slash commands (`/link`, `/senpai`, `/inbox`, `/goal`, `/plan`, `/learn`, `/deepresearch`, `/boost`) with full parameter templates and recommended arguments.
     - **Context & History Grounding:** Prioritize recent workspace symbols, modified file paths, active git branch names, and words from `~/.config/reaper-notes/user_vocabulary.db`.

4. **Zero-Friction Prompt Completion:**
   - When a user prompt appears truncated, hurried, or cut off mid-thought, infer the completed sentence based on recent trajectory, confirm silently, and execute without hesitation.
