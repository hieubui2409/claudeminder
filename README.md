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
git clone https://github.com/yourusername/claudiminder.git
cd claudiminder

# Install Python dependencies
uv sync

# Run TUI
uv run claudiminder status
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
claudiminder status

# Show as JSON
claudiminder status --json

# Launch TUI
claudiminder tui

# Show version
claudiminder version
```

## Configuration

Configuration is stored in `~/.config/claudiminder/config.toml`.

OAuth credentials are automatically grabbed from `~/.claude/.credentials.json`.

## Themes

- Light / Dark (standard)
- Neon Light / Neon Dark (vibrant)
- Glassmorphism Light / Dark (frosted glass effect)

## License

MIT
