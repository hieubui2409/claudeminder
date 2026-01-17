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

### Testing

```bash
# Run backend tests
uv run pytest tests/backend

# Run frontend tests
cd src/frontend && bun run test

# Run with coverage
uv run pytest tests/backend --cov=src/backend
```

### Building

```bash
# Build Tauri app (Linux)
cd src/frontend && bun run tauri build

# Build Python package
uv build

# Build Python sidecar binary (Nuitka)
./scripts/build-sidecar.sh
```

### E2E Testing

```bash
# Install Playwright browsers
cd src/frontend && bunx playwright install chromium

# Run E2E tests
bun run test:e2e
```

### Pre-commit Hooks

```bash
# Install pre-commit hooks
uv run pre-commit install

# Run hooks manually
uv run pre-commit run --all-files
```

## CI/CD

- **Test workflow**: Runs on push/PR to main/master
- **Build workflow**: Cross-platform builds (Linux, macOS, Windows)
- **Release workflow**: Automatic releases on version tags (v\*)

## License

MIT
