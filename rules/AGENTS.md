# Antigravity Fuzzy Autocorrect & Intent Interpretation Rule

1. **Typo Tolerance & Automatic Spellcheck:**
   - When the user types prompts with typos, missing letters, inverted characters (e.g. `tehn`, `reusme`, `lfet`, `suod`, `whcih`), silently autocorrect them to the intended words using Levenshtein minimum distance.
   - Never ask for clarification on obvious typos; resolve them automatically and proceed.

2. **Predictive Shorthand & Intent Expansion:**
   - Expand shorthand abbreviations into complete operations.
   - If the user provides a brief or fragmented instruction, infer the complete pair-programming objective based on recent session context and execute thoroughly.
