# Development Rules

This directory contains development rules and coding standards for claudiminder.

## Files

| File               | Scope                 | Description                        |
| ------------------ | --------------------- | ---------------------------------- |
| `00-principles.md` | All code              | Core principles (YAGNI, KISS, DRY) |
| `01-python.md`     | `src/backend/**/*.py` | Python coding standards            |
| `02-tauri.md`      | `src/frontend/**/*`   | Tauri v2 & frontend rules          |

## How to Use

1. Read all rules before starting development
2. Follow the patterns in each rule file
3. When in doubt, refer back to these documents

## Quick Reference

### Python (Backend)

- Python 3.12+ with type hints
- Use `pydantic-settings` for config
- Use `httpx` + `tenacity` for HTTP
- Use `loguru` for logging

### Tauri (Frontend)

- Tauri v2 with React + TypeScript
- Use system tray for background mode
- Python sidecar for backend logic
- Minimal Rust commands, delegate to sidecar
