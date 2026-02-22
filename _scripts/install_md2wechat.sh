#!/usr/bin/env bash
# Install official md2wechat binary from geekjourneyx/md2wechat-skill
# Usage: ./install_md2wechat.sh [install-dir]
# Default: ~/.local/bin (or _scripts/bin if run from vault)

set -e
VERSION="v1.9.0"
REPO="https://github.com/geekjourneyx/md2wechat-skill/releases/download"
INSTALL_DIR="${1:-$HOME/.local/bin}"

# Detect platform
OS=$(uname -s | tr '[:upper:]' '[:lower:]')
ARCH=$(uname -m)
case "$ARCH" in
  x86_64|amd64) ARCH="amd64" ;;
  arm64|aarch64) ARCH="arm64" ;;
  *) echo "Unsupported architecture: $ARCH"; exit 1 ;;
esac

case "$OS" in
  darwin) BINARY="md2wechat-darwin-$ARCH" ;;
  linux)  BINARY="md2wechat-linux-$ARCH" ;;
  *) echo "Unsupported OS: $OS"; exit 1 ;;
esac

URL="$REPO/$VERSION/$BINARY"
mkdir -p "$INSTALL_DIR"
echo "Downloading $BINARY..."
curl -fsSL -o "$INSTALL_DIR/md2wechat-bin" "$URL"
chmod +x "$INSTALL_DIR/md2wechat-bin"
# Install wrapper (fixes digest 120-char bug for --draft --cover)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cp "$SCRIPT_DIR/md2wechat" "$INSTALL_DIR/md2wechat"
chmod +x "$INSTALL_DIR/md2wechat"
echo "✓ Installed md2wechat (with digest fix) to $INSTALL_DIR/md2wechat"
echo "  Add to PATH if needed: export PATH=\"$INSTALL_DIR:\$PATH\""
"$INSTALL_DIR/md2wechat" --help >/dev/null 2>&1 && echo "✓ md2wechat works" || true
