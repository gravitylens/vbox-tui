#!/usr/bin/env bash
# Build script for vbox-tui binary distribution

set -e

echo "Building vbox-tui binary..."

# Clean previous builds
rm -rf build dist

# Build with PyInstaller
pyinstaller --clean vbox-tui.spec

# Check if build was successful
if [ -f dist/vbox-tui ]; then
    echo ""
    echo "✓ Build successful!"
    echo "Binary location: dist/vbox-tui"
    echo "Binary size: $(du -h dist/vbox-tui | cut -f1)"
    echo ""
    echo "You can run it with: ./dist/vbox-tui"
    echo "Or install it to your PATH: sudo cp dist/vbox-tui /usr/local/bin/"
else
    echo "✗ Build failed!"
    exit 1
fi
