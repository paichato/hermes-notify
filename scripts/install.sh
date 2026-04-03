#!/bin/bash
# hermes-notify installer
# Usage: curl -fsSL https://raw.githubusercontent.com/paichato/hermes-notify/main/scripts/install.sh | bash

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
CYAN='\033[0;36m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# GitHub repo (override with: HERMES_NOTIFY_REPO=username/repo)
REPO="${HERMES_NOTIFY_REPO:-paichato/hermes-notify}"
BRANCH="${HERMES_NOTIFY_BRANCH:-main}"

print_header() {
    echo ""
    echo -e "${CYAN}╔══════════════════════════════════════════════╗${NC}"
    echo -e "${CYAN}║                                              ║${NC}"
    echo -e "${CYAN}║       🤖 Installing hermes-notify 🤖         ║${NC}"
    echo -e "${CYAN}║                                              ║${NC}"
    echo -e "${CYAN}╚══════════════════════════════════════════════╝${NC}"
    echo ""
}

check_python() {
    if command -v python3 &> /dev/null; then
        PYTHON=python3
    elif command -v python &> /dev/null; then
        PYTHON=python
    else
        echo -e "${RED}✗ Python 3 is required but not found.${NC}"
        echo "  Please install Python 3 and try again."
        echo "  https://www.python.org/downloads/"
        exit 1
    fi
    
    # Check Python version
    PY_VERSION=$($PYTHON -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
    PY_MAJOR=$($PYTHON -c 'import sys; print(sys.version_info.major)')
    
    if [ "$PY_MAJOR" -lt 3 ]; then
        echo -e "${RED}✗ Python 3.9+ required, found Python $PY_VERSION${NC}"
        exit 1
    fi
    
    echo -e "${GREEN}✓${NC} Python $PY_VERSION found"
}

check_pip() {
    if ! $PYTHON -m pip --version &> /dev/null; then
        echo -e "${YELLOW}⚠ pip not found, installing...${NC}"
        $PYTHON -m ensurepip --upgrade 2>/dev/null || {
            echo -e "${RED}✗ Could not install pip. Please install manually.${NC}"
            exit 1
        }
    fi
    echo -e "${GREEN}✓${NC} pip available"
}

install_package() {
    echo ""
    echo -e "${CYAN}Installing hermes-notify...${NC}"
    
    # Try pip install from GitHub (with flags for various Python setups)
    $PYTHON -m pip install "git+https://github.com/$REPO.git@$BRANCH" --break-system-packages 2>/dev/null || \
    $PYTHON -m pip install "git+https://github.com/$REPO.git@$BRANCH" --user 2>/dev/null || \
    $PYTHON -m pip install "git+https://github.com/$REPO.git@$BRANCH" --user --break-system-packages 2>/dev/null || {
        echo -e "${RED}✗ Installation failed${NC}"
        echo ""
        echo "Try manually:"
        echo "  pip install hermes-notify --break-system-packages"
        echo "  or"
        echo "  pip install hermes-notify --user"
        exit 1
    }
    
    echo -e "${GREEN}✓${NC} hermes-notify installed"
}

run_setup() {
    echo ""
    echo -e "${CYAN}Running setup wizard...${NC}"
    echo ""
    
    if command -v hermes-notify-setup &> /dev/null; then
        hermes-notify-setup
    else
        # Fallback: run module directly
        $PYTHON -m hermes_notify.installer
    fi
}

print_success() {
    echo ""
    echo -e "${GREEN}╔══════════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║            ✅ Installation Complete!         ║${NC}"
    echo -e "${GREEN}╚══════════════════════════════════════════════╝${NC}"
    echo ""
    echo -e "Usage:"
    echo -e "  ${CYAN}hermes-notify${NC} \"Task complete!\""
    echo -e "  ${CYAN}hermes-notify${NC} --status"
    echo -e "  ${CYAN}hermes-notify${NC} --config"
    echo ""
    echo -e "Shell integration (optional):"
    echo -e "  ${CYAN}hermes-notify${NC} --install-prompt"
    echo ""
}

# Main
main() {
    print_header
    check_python
    check_pip
    install_package
    
    # Ask if user wants to run setup
    echo ""
    read -p "Run setup wizard now? [Y/n]: " -n 1 -r
    echo ""
    if [[ $REPLY =~ ^[Nn]$ ]]; then
        echo -e "${YELLOW}Skipped setup. Run 'hermes-notify-setup' later.${NC}"
    else
        run_setup
    fi
    
    print_success
}

main
