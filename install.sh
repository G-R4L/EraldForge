#!/data/data/com.termux/files/usr/bin/env bash
set -e

echo ">>> EraldForge installer for Termux"
echo "Updating packages..."
pkg update -y && pkg upgrade -y

echo "Installing required packages..."
pkg install -y python git wget nano nmap termux-api

# pip packages
pip install --upgrade pip
pip install python-dateutil pyqrcode pillow qrcode

# Prepare install dir
TARGET="$HOME/eraldforge"
if [ -d "$TARGET" ]; then
  echo "Found existing $TARGET — backing up"
  mv "$TARGET" "${TARGET}_backup_$(date +%s)"
fi

echo "Copying project files to $TARGET"
cp -r . "$TARGET"
chmod +x "$TARGET"/launcher.py
for f in "$TARGET"/tools/*/*.py; do
  chmod +x "$f"
done

# Symlink launcher to PATH
PREFIX=${PREFIX:-/data/data/com.termux/files/usr}
ln -sf "$TARGET/launcher.py" "$PREFIX/bin/eraldforge"
echo "Installed. Run 'eraldforge' to start the launcher."

echo "Run 'termux-setup-storage' once if you need access to storage."
