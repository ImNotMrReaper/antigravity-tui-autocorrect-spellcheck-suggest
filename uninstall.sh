#!/usr/bin/env bash
# ==============================================================================
# agy-suggest: Antigravity TUI Autocorrect, Spell Checker & Suggestive Text Engine Clean Uninstaller
# Remote 1-Liner:
#   curl -fsSL https://raw.githubusercontent.com/ImNotMrReaper/agy-suggest/main/uninstall.sh | bash
# ==============================================================================

set -e

RED="\033[91m"
GREEN="\033[92m"
CYAN="\033[96m"
RESET="\033[0m"

echo -e "${CYAN}>>> Uninstalling agy-suggest: Antigravity TUI Autocorrect, Spell Checker & Suggestive Text Engine...${RESET}"

rm -rf "${HOME}/.gemini/config/plugins/agy-suggest"
rm -rf "${HOME}/.gemini/config/plugins/tui-autocomplete"
rm -rf "${HOME}/.gemini/config/plugins/antigravity-tui-autocorrect-spellcheck-suggest"
rm -rf "${HOME}/.gemini/antigravity-cli/plugin_data/agy-suggest"
rm -rf "${HOME}/.gemini/antigravity-cli/plugin_data/tui-autocomplete"
rm -rf "${HOME}/.gemini/antigravity-cli/plugin_data/antigravity-tui-autocorrect-spellcheck-suggest"
rm -rf "${HOME}/.agents/skills/agy-suggest"
rm -rf "${HOME}/.agents/skills/tui-autocomplete-suggest"

for cmd in tui-autocorrect antigravity-tui-autocorrect agy-autocorrect agy-suggest; do
    if [ -f "/usr/local/bin/$cmd" ]; then
        if [ -w "/usr/local/bin" ] || [ "$(id -u)" -eq 0 ]; then
            rm -f "/usr/local/bin/$cmd"
        elif command -v sudo >/dev/null 2>&1; then
            sudo rm -f "/usr/local/bin/$cmd"
        fi
    fi
    rm -f "${HOME}/.local/bin/$cmd"
done
rm -f "${HOME}/.local/bin/agy-tui"

# Restore original agy binary if wrapped
if [ -f "${HOME}/.local/bin/agy.real" ]; then
    mv -f "${HOME}/.local/bin/agy.real" "${HOME}/.local/bin/agy"
    echo -e "    ${GREEN}✓ Restored original AGY binary:${RESET} ${HOME}/.local/bin/agy"
fi

echo -e "${GREEN}✓ Antigravity TUI Autocorrect, Spell Checker & Suggestive Text Engine cleanly uninstalled.${RESET}\n"
