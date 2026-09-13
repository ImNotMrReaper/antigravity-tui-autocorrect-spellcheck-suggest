#!/usr/bin/env bash
# ==============================================================================
# Antigravity TUI Autocomplete & Suggestive Text Engine Installer
# Remote 1-Liner:
#   curl -fsSL https://raw.githubusercontent.com/ImNotMrReaper/tui-autocomplete/main/install.sh | bash
# ==============================================================================

set -e

# ANSI Styling
BOLD="\033[1m"
CYAN="\033[96m"
PURPLE="\033[95m"
GREEN="\033[92m"
YELLOW="\033[93m"
RED="\033[91m"
RESET="\033[0m"

echo -e "${PURPLE}================================================================${RESET}"
echo -e "${BOLD} ⚡ Antigravity TUI Autocomplete & Suggestive Text Engine${RESET}"
echo -e "${PURPLE}================================================================${RESET}\n"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" 2>/dev/null && pwd)"

# Auto-clone repository if executed directly from curl/pipe
if [ ! -d "${SCRIPT_DIR}/scripts" ] || [ ! -f "${SCRIPT_DIR}/scripts/tui_autocorrect.py" ]; then
    echo -e "${CYAN}>>> Running from remote pipe. Cloning latest repository...${RESET}"
    TMP_CLONE="$(mktemp -d /tmp/tui-autocomplete-install.XXXXXX)"
    if ! command -v git >/dev/null 2>&1; then
        echo ">>> Installing git..."
        if command -v apt-get >/dev/null 2>&1; then
            if [ "$(id -u)" -eq 0 ]; then apt-get update -qq && apt-get install -y -qq git; else sudo apt-get update -qq && sudo apt-get install -y -qq git; fi
        elif command -v dnf >/dev/null 2>&1; then
            if [ "$(id -u)" -eq 0 ]; then dnf install -y git; else sudo dnf install -y git; fi
        elif command -v pacman >/dev/null 2>&1; then
            if [ "$(id -u)" -eq 0 ]; then pacman -Sy --needed --noconfirm git; else sudo pacman -Sy --needed --noconfirm git; fi
        elif command -v zypper >/dev/null 2>&1; then
            if [ "$(id -u)" -eq 0 ]; then zypper --non-interactive install git; else sudo zypper --non-interactive install git; fi
        fi
    fi
    git clone --depth 1 https://github.com/ImNotMrReaper/tui-autocomplete.git "${TMP_CLONE}"
    SCRIPT_DIR="${TMP_CLONE}"
    trap "rm -rf '${TMP_CLONE}'" EXIT
fi

# Ensure Python 3 is installed
if ! command -v python3 >/dev/null 2>&1; then
    echo -e "${YELLOW}>>> Python 3 not found. Installing Python 3...${RESET}"
    if command -v apt-get >/dev/null 2>&1; then
        if [ "$(id -u)" -eq 0 ]; then apt-get update -qq && apt-get install -y -qq python3; else sudo apt-get update -qq && sudo apt-get install -y -qq python3; fi
    elif command -v dnf >/dev/null 2>&1; then
        if [ "$(id -u)" -eq 0 ]; then dnf install -y python3; else sudo dnf install -y python3; fi
    elif command -v pacman >/dev/null 2>&1; then
        if [ "$(id -u)" -eq 0 ]; then pacman -Sy --needed --noconfirm python; else sudo pacman -Sy --needed --noconfirm python; fi
    elif command -v zypper >/dev/null 2>&1; then
        if [ "$(id -u)" -eq 0 ]; then zypper --non-interactive install python3; else sudo zypper --non-interactive install python3; fi
    fi
fi

PLUGIN_DIR="${HOME}/.gemini/config/plugins/tui-autocomplete"
SKILLS_DIR="${HOME}/.agents/skills/tui-autocomplete-suggest"

echo -e "${CYAN}>>> Installing Antigravity Plugin & Skills...${RESET}"
mkdir -p "${PLUGIN_DIR}"
cp -r "${SCRIPT_DIR}/"* "${PLUGIN_DIR}/" 2>/dev/null || true

if [ -d "${SCRIPT_DIR}/skills/tui-autocomplete-suggest" ]; then
    mkdir -p "${SKILLS_DIR}"
    cp -r "${SCRIPT_DIR}/skills/tui-autocomplete-suggest/"* "${SKILLS_DIR}/" 2>/dev/null || true
    echo -e "    ${GREEN}✓ Installed Agent Skill:${RESET} ${SKILLS_DIR}"
fi

# Install CLI binary wrapper
echo -e "\n${CYAN}>>> Installing CLI command (tui-autocorrect)...${RESET}"
CLI_TARGET=""
if [ -w "/usr/local/bin" ] || [ "$(id -u)" -eq 0 ]; then
    CLI_TARGET="/usr/local/bin/tui-autocorrect"
elif command -v sudo >/dev/null 2>&1; then
    sudo mkdir -p /usr/local/bin
    CLI_TARGET="/usr/local/bin/tui-autocorrect"
else
    mkdir -p "${HOME}/.local/bin"
    CLI_TARGET="${HOME}/.local/bin/tui-autocorrect"
fi

cat << 'EOF_WRAPPER' > /tmp/tui-autocorrect-wrapper
#!/usr/bin/env bash
PLUGIN_SCRIPT="${HOME}/.gemini/config/plugins/tui-autocomplete/scripts/tui_autocorrect.py"
if [ -f "$PLUGIN_SCRIPT" ]; then
    exec python3 "$PLUGIN_SCRIPT" "$@"
else
    echo "Error: tui_autocorrect.py not found at $PLUGIN_SCRIPT" >&2
    exit 1
fi
EOF_WRAPPER
chmod +x /tmp/tui-autocorrect-wrapper

if [ -w "$(dirname "$CLI_TARGET")" ]; then
    mv /tmp/tui-autocorrect-wrapper "$CLI_TARGET"
else
    sudo mv /tmp/tui-autocorrect-wrapper "$CLI_TARGET"
fi
echo -e "    ${GREEN}✓ Installed CLI Wrapper:${RESET} ${CLI_TARGET}"

echo -e "\n${GREEN}================================================================${RESET}"
echo -e "${GREEN} 🎉 TUI AUTOCOMPLETE ENGINE INSTALLED SUCCESSFULLY!${RESET}"
echo -e "${GREEN}================================================================${RESET}"
echo -e "Features active:"
echo -e "  • Antigravity Plugin:  ${PLUGIN_DIR}"
echo -e "  • Agent Skill:         ${SKILLS_DIR}"
echo -e "  • Terminal CLI Tool:   ${CLI_TARGET}"
echo -e ""
echo -e "Quick Test:"
echo -e "  ${PURPLE}tui-autocorrect tehn antigravty autocompleate suod reusme${RESET}"
echo -e "  Output: ${GREEN}then antigravity autocomplete sudo resume${RESET}\n"
