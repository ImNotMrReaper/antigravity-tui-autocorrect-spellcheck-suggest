#!/usr/bin/env bash
# ==============================================================================
# Antigravity TUI Autocomplete Clean Uninstaller
# Remote 1-Liner:
#   curl -fsSL https://raw.githubusercontent.com/ImNotMrReaper/tui-autocomplete/main/uninstall.sh | bash
# ==============================================================================

set -e

RED="\033[91m"
GREEN="\033[92m"
CYAN="\033[96m"
RESET="\033[0m"

echo -e "${CYAN}>>> Uninstalling Antigravity TUI Autocomplete...${RESET}"

rm -rf "${HOME}/.gemini/config/plugins/tui-autocomplete"
rm -rf "${HOME}/.agents/skills/tui-autocomplete-suggest"

if [ -f "/usr/local/bin/tui-autocorrect" ]; then
    if [ -w "/usr/local/bin" ] || [ "$(id -u)" -eq 0 ]; then
        rm -f "/usr/local/bin/tui-autocorrect"
    elif command -v sudo >/dev/null 2>&1; then
        sudo rm -f "/usr/local/bin/tui-autocorrect"
    fi
fi
rm -f "${HOME}/.local/bin/tui-autocorrect"
rm -f "${HOME}/.local/bin/agy-tui"

# Restore original agy binary if wrapped
if [ -f "${HOME}/.local/bin/agy.real" ]; then
    mv -f "${HOME}/.local/bin/agy.real" "${HOME}/.local/bin/agy"
    echo -e "    ${GREEN}✓ Restored original AGY binary:${RESET} ${HOME}/.local/bin/agy"
fi

echo -e "${GREEN}✓ Antigravity TUI Autocomplete cleanly uninstalled.${RESET}\n"
