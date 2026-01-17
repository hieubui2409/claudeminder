#!/bin/bash
# Build Python sidecar as standalone binary using Nuitka

set -e

cd "$(dirname "$0")/.."

echo "Building claudeminder sidecar with Nuitka..."

# Install build dependencies
uv sync --extra build

# Determine output name based on platform
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
    OUTPUT_NAME="claudeminder-sidecar.exe"
    PLATFORM="windows"
elif [[ "$OSTYPE" == "darwin"* ]]; then
    OUTPUT_NAME="claudeminder-sidecar"
    PLATFORM="macos"
else
    OUTPUT_NAME="claudeminder-sidecar"
    PLATFORM="linux"
fi

# Build with Nuitka
uv run python -m nuitka \
    --standalone \
    --onefile \
    --follow-imports \
    --include-package=claudeminder \
    --include-data-dir=src/claudeminder/i18n=claudeminder/i18n \
    --output-filename=$OUTPUT_NAME \
    --output-dir=dist/sidecar-$PLATFORM \
    --assume-yes-for-downloads \
    --remove-output \
    src/claudeminder/sidecar.py

echo "Built: dist/sidecar-$PLATFORM/$OUTPUT_NAME"

# Copy to Tauri sidecar location
SIDECAR_DIR="src/frontend/src-tauri/binaries"
mkdir -p "$SIDECAR_DIR"

if [[ "$PLATFORM" == "linux" ]]; then
    TARGET_TRIPLE="x86_64-unknown-linux-gnu"
elif [[ "$PLATFORM" == "macos" ]]; then
    TARGET_TRIPLE="x86_64-apple-darwin"
else
    TARGET_TRIPLE="x86_64-pc-windows-msvc"
fi

cp "dist/sidecar-$PLATFORM/$OUTPUT_NAME" "$SIDECAR_DIR/claudeminder-sidecar-$TARGET_TRIPLE"
echo "Copied to: $SIDECAR_DIR/claudeminder-sidecar-$TARGET_TRIPLE"
