#!/usr/bin/env python3
"""
tui_autocorrect.py: Fast Levenshtein distance spellchecker & suggestive text engine
for Antigravity terminal sessions and prompt typing.
"""

import sys
from typing import List, Optional, Tuple

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
    "antigravty": "antigravity",
    "autocompleate": "autocomplete",
    "suod": "sudo",
    "reusme": "resume",
    "improt": "import",
    "seledt": "select",
    "valut": "vault",
}


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

    best_match = word
    min_dist = 3
    for candidate in DICTIONARY:
        dist = levenshtein(lower, candidate)
        if dist < min_dist:
            min_dist = dist
            best_match = candidate

    return best_match if min_dist <= 2 else word


if __name__ == "__main__":
    if len(sys.argv) > 1:
        words = sys.argv[1:]
        corrected = [correct_word(w) for w in words]
        print(" ".join(corrected))
    else:
        print("Usage: tui_autocorrect.py <word1> [word2...]")
