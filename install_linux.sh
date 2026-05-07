#!/bin/bash

# PyLock Install Script
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="$PROJECT_DIR/.venv"
SCRIPT_PATH="$PROJECT_DIR/pylock.py"

echo "Create virtual envoirment..."
python3 -m venv "$VENV_DIR"

echo "Install dependencies..."
source "$VENV_DIR/bin/activate"
pip install --upgrade pip
pip install -r requirements.txt

# Create alias
ALIAS_CMD="alias pylock='$VENV_DIR/bin/python \"$SCRIPT_PATH\"'"

# Enlist in.zshrc or.bashrc
    CONFIG="$HOME/.zshrc"
elif [[ -f "$HOME/.bashrc" ]]; then
    CONFIG="$HOME/.bashrc"
else
    echo "Couldn't find a shell config."
    echo "Add manually: $ALIAS_CMD"
    exit 0
fi

# Remove an old alias and add a new one
sed -i '/alias pylock=/d' "$CONFIG" 2>/dev/null
echo "" >> "$CONFIG"
echo "# PyLock Alias" >> "$CONFIG"
echo "$ALIAS_CMD" >> "$CONFIG"

echo "Installation complete."
echo "Alias 'pylock' has been set up."
echo "Run: source $CONFIG"