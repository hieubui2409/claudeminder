# Claudeminder

Claude usage tracking & reminder tool with TUI/GUI support for Linux, Windows, and macOS.

## Features

- 📊 Real-time usage tracking via Anthropic OAuth API
- ⏰ 5-hour window reset time display & reminders
- 🔔 Preset reminder strategies (before reset, on reset, custom intervals)
- 🖥️ System tray icon with usage percentage + hover for reset time
- 🔐 Auto-open Claude login when token expired
- 💻 TUI mode for terminal usage
- 🎨 GUI mode via Tauri v2 with multiple themes

## Tech Stack

- **Backend**: Python 3.12+ (loguru, pydantic-settings, httpx, tenacity)
- **Frontend**: TypeScript + React + Tauri v2
- **Build**: uv (Python), Cargo (Rust), bun (frontend)

## Quick Start

### Prerequisites

- Python 3.12+
- uv (Python package manager)
- Rust + Cargo
- Bun (for frontend)

### Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/claudeminder.git
cd claudeminder

# Install Python dependencies
uv sync

# Run TUI
uv run claudeminder status
```

### GUI Mode (Tauri)

```bash
cd src/frontend
bun install
bun run tauri dev
```

## Usage

### CLI Commands

```bash
# Show usage status
claudeminder status

# Show as JSON
claudeminder status --json

# Launch TUI
claudeminder tui

# Show version
claudeminder version
```

## Configuration

Configuration is stored in `~/.config/claudeminder/config.toml`.

OAuth credentials are automatically grabbed from `~/.claude/.credentials.json`.

## Themes

- Light / Dark (standard)
- Neon Light / Neon Dark (vibrant)
- Glassmorphism Light / Dark (frosted glass effect)

## Development

### Quick Commands

```bash
# Navigate to frontend directory
cd src/frontend

# Install dependencies (first time only)
bun install

# ─────────────────────────────────────────────────────────
# DEVELOPMENT
# ─────────────────────────────────────────────────────────

# Run Tauri app in dev mode (hot reload)
bun run tauri dev

# Run Vite dev server only (without Tauri)
bun run dev

# Preview production build locally
bun run preview

# ─────────────────────────────────────────────────────────
# BUILD
# ─────────────────────────────────────────────────────────

# Build frontend only (TypeScript + Vite)
bun run build

# Build Tauri app (creates executable)
bun run tauri build

# Build outputs:
# - Linux: src/frontend/src-tauri/target/release/bundle/
#   - .deb package
#   - .AppImage
# - macOS: .app bundle, .dmg
# - Windows: .exe, .msi

# ─────────────────────────────────────────────────────────
# TESTING
# ─────────────────────────────────────────────────────────

# Run unit tests
bun run test

# Run tests with coverage
bun run test:coverage

# Run E2E tests (requires Playwright)
bunx playwright install chromium  # first time only
bun run test:e2e

# ─────────────────────────────────────────────────────────
# CODE QUALITY
# ─────────────────────────────────────────────────────────

# Type check
bun run typecheck

# Lint
bun run lint

# Format code
bun run format

# Check formatting
bun run format:check
```

### Backend (Python)

```bash
# From project root
uv sync                              # Install dependencies
uv run pytest tests/backend          # Run tests
uv run pytest --cov=src/backend      # Run with coverage
uv build                             # Build Python package
```

### Pre-commit Hooks

```bash
uv run pre-commit install            # Install hooks
uv run pre-commit run --all-files    # Run manually
```

## CI/CD

- **Test workflow**: Runs on push/PR to main/master
- **Build workflow**: Cross-platform builds (Linux, macOS, Windows)
- **Release workflow**: Automatic releases on version tags (v\*)

## License

MIT
