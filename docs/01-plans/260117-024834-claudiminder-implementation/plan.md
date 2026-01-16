---
title: "Claudiminder Full Implementation"
description: "Complete TUI + GUI implementation with Textual, Tauri v2, themes, reminders"
status: pending
priority: P1
effort: 30h
branch: main
tags: [textual, tauri, react, tui, gui, themes, reminders, nuitka, i18n]
created: 2026-01-17
updated: 2026-01-17
---

# Claudiminder Implementation Plan

## Overview

Complete implementation of Claude usage tracking tool with dual interfaces:

- **TUI**: Textual-based terminal dashboard (simple ANSI colors)
- **GUI**: Tauri v2 + React desktop app (6 themes, customizable UI)
- **macOS**: Menu bar app + Touch Bar support

## Requirements

- [Requirements Summary](./requirements-summary.md) - 48 interview questions answered

## Research Reports

- [Tauri v2 Features](../reports/researcher-260117-024702-tauri-v2-features.md)
- [Python TUI Libraries](../reports/researcher-260117-024702-python-tui-libraries.md)
- [UI Themes Design](../reports/researcher-260117-024115-ui-themes-design.md)

## Phases

| Phase | Title                                          | Status  | Effort | Description                                  |
| ----- | ---------------------------------------------- | ------- | ------ | -------------------------------------------- |
| 1     | [Backend Core](./phase-01-backend-core.md)     | pending | 6h     | TUI, scheduler, focus mode, goals, i18n      |
| 2     | [Tauri Scaffold](./phase-02-tauri-scaffold.md) | pending | 4h     | Tauri v2 + React + macOS menu bar            |
| 3     | [Frontend UI](./phase-03-frontend-ui.md)       | pending | 8h     | Customizable UI, 6 themes, drag-drop         |
| 4     | [Integration](./phase-04-integration.md)       | pending | 6h     | Nuitka sidecar, cert pinning, notifications  |
| 5     | [Testing](./phase-05-testing.md)               | pending | 6h     | 90% coverage, Playwright E2E, mypy + pyright |

## Key Dependencies

- Python 3.12+, uv, Textual 1.0+, Nuitka
- Rust, Cargo, Tauri v2
- Bun, React 18+, TypeScript, Playwright

## Architecture

```
src/
├── backend/          # Python (existing + TUI)
│   ├── api/          # Usage API client
│   ├── models/       # Pydantic models
│   ├── utils/        # Credentials
│   ├── tui/          # NEW: Textual TUI
│   ├── scheduler/    # NEW: Reminder scheduler
│   └── cli.py        # Entry point
└── frontend/         # NEW: Tauri + React
    ├── src/          # React app
    └── src-tauri/    # Rust backend
```

## Success Criteria

- [ ] TUI displays usage % + reset time in real-time (simple ANSI)
- [ ] GUI shows all metrics with 6 themes + customizable layout
- [ ] System tray: configurable icon style, full tooltip, complete menu
- [ ] Reminders: all presets + custom shell/URL + snooze support
- [ ] Focus mode: DND when high usage + scheduled quiet hours
- [ ] Goals: daily budget + pace indicator
- [ ] i18n: English + Vietnamese
- [ ] macOS: menu bar app + Touch Bar support
- [ ] Single instance enforcement
- [ ] Offline mode UI when no network
- [ ] 90%+ test coverage, E2E with Playwright
- [ ] Cross-platform: Linux, Windows, macOS
