#!/bin/bash
set -e

# Build Python sidecar using Nuitka for Tauri integration
# This script detects the target platform and builds a standalone binary

# Detect target triple based on OS and architecture
detect_target() {
    local os=$(uname -s)
    local arch=$(uname -m)

    case "${os}-${arch}" in
        Linux-x86_64)
            echo "x86_64-unknown-linux-gnu"
            ;;
        Linux-aarch64)
            echo "aarch64-unknown-linux-gnu"
            ;;
        Darwin-x86_64)
            echo "x86_64-apple-darwin"
            ;;
        Darwin-arm64)
            echo "aarch64-apple-darwin"
            ;;
        MINGW*-x86_64|MSYS*-x86_64|CYGWIN*-x86_64)
            echo "x86_64-pc-windows-msvc"
            ;;
        *)
            echo "ERROR: Unsupported platform: ${os}-${arch}" >&2
            exit 1
            ;;
    esac
}

# Get file extension for Windows
get_extension() {
    if [[ "$(uname -s)" =~ ^(MINGW|MSYS|CYGWIN) ]]; then
        echo ".exe"
    else
        echo ""
    fi
}

TARGET=$(detect_target)
EXT=$(get_extension)
OUTPUT_NAME="claudeminder-backend-${TARGET}${EXT}"

echo "========================================="
echo "Building claudeminder sidecar with Nuitka"
echo "========================================="
echo "Platform: $(uname -s) $(uname -m)"
echo "Target: ${TARGET}"
echo "Output: ${OUTPUT_NAME}"
echo "========================================="
echo ""

# Navigate to project root
cd "$(dirname "$0")/.."

# Ensure Nuitka is installed
echo "Checking Nuitka installation..."
if ! uv run python -c "import nuitka" 2>/dev/null; then
    echo "Installing Nuitka..."
    uv add --dev nuitka
fi

# Build with Nuitka
echo ""
echo "Building with Nuitka (this may take a few minutes)..."
echo ""

uv run nuitka \
    --standalone \
    --onefile \
    --output-filename="${OUTPUT_NAME}" \
    --enable-plugin=anti-bloat \
    --assume-yes-for-downloads \
    --remove-output \
    --quiet \
    src/claudeminder/sidecar.py

# Check build result
if [ ! -f "${OUTPUT_NAME}" ]; then
    echo "ERROR: Build failed - ${OUTPUT_NAME} not found" >&2
    exit 1
fi

# Create binaries directory for Tauri
BINARIES_DIR="src/frontend/src-tauri/binaries"
mkdir -p "${BINARIES_DIR}"

# Copy binary to Tauri binaries directory
echo "Copying binary to ${BINARIES_DIR}/"
cp "${OUTPUT_NAME}" "${BINARIES_DIR}/"

# Make executable on Unix-like systems
if [[ ! "$(uname -s)" =~ ^(MINGW|MSYS|CYGWIN) ]]; then
    chmod +x "${BINARIES_DIR}/${OUTPUT_NAME}"
fi

# Get file size
FILE_SIZE=$(du -h "${BINARIES_DIR}/${OUTPUT_NAME}" | cut -f1)

echo ""
echo "========================================="
echo "Build successful!"
echo "========================================="
echo "Output: ${BINARIES_DIR}/${OUTPUT_NAME}"
echo "Size: ${FILE_SIZE}"
echo "========================================="
echo ""

# Test the binary
echo "Testing binary..."
if "${BINARIES_DIR}/${OUTPUT_NAME}" check_token > /dev/null 2>&1; then
    echo "✓ Binary test passed"
else
    echo "⚠ Binary test returned non-zero exit code (may be normal if no token present)"
fi

echo ""
echo "Done! Binary ready for Tauri integration."
