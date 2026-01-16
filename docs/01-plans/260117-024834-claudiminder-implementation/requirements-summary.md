# Requirements Summary (from Interview)

**Date:** 2026-01-17 | **Questions:** 48

---

## Core Functionality

| Aspect           | Decision                            |
| ---------------- | ----------------------------------- |
| Primary mode     | Equal priority (TUI + GUI)          |
| Polling strategy | Hybrid (60s auto + manual refresh)  |
| Token expired    | Notification + button to open login |
| Run mode         | Optional startup (user setting)     |

## Reminder System

| Aspect             | Decision                                                       |
| ------------------ | -------------------------------------------------------------- |
| Preset strategies  | All: before reset (15/30/60m), on reset, percentage thresholds |
| Custom action      | Shell command OR URL                                           |
| Notification style | All: system native + in-app toast + TUI bell                   |
| Snooze             | Yes, with 5/15/30 min options                                  |

## UI/UX Themes

| Aspect        | Decision                                      |
| ------------- | --------------------------------------------- |
| Default theme | Neon Dark                                     |
| Custom colors | Layered: preset → accent → full customization |
| TUI style     | Simple terminal (ANSI colors)                 |
| Window size   | Resizable                                     |

## System Tray

| Aspect     | Decision                                     |
| ---------- | -------------------------------------------- |
| Icon style | Configurable: number + progress + color      |
| Tooltip    | Full details (usage %, reset time, requests) |
| Menu       | Full: Show, Refresh, Settings, About, Quit   |
| Animation  | Pulse on notification (cross-platform safe)  |

## Configuration

| Aspect        | Decision                |
| ------------- | ----------------------- |
| Format        | TOML                    |
| Location      | ~/.config/claudiminder/ |
| Export/Import | No                      |
| Usage history | No                      |

## Build & Deployment

| Aspect       | Decision                                      |
| ------------ | --------------------------------------------- |
| Python build | Nuitka compiled                               |
| Distribution | GitHub Releases only                          |
| CI/CD        | Full pipeline (test + build + sign + publish) |
| Code signing | Later decision                                |

## Error Handling

| Aspect          | Decision                      |
| --------------- | ----------------------------- |
| Log level       | User configurable             |
| Log output      | Stdout + file                 |
| Error recovery  | Retry → toast → degraded mode |
| Crash reporting | No telemetry                  |

## Keyboard & Accessibility

| Aspect        | Decision                        |
| ------------- | ------------------------------- |
| Global hotkey | User customizable               |
| TUI shortcuts | Basic (q/r/h)                   |
| Accessibility | Basic a11y (ARIA, keyboard nav) |
| Font size     | Slider (80%-150%)               |

## API & Integration

| Aspect          | Decision                                       |
| --------------- | ---------------------------------------------- |
| Local API       | None                                           |
| Credentials     | Claude file only (~/.claude/.credentials.json) |
| CLI integration | None (standalone)                              |

## Testing & Quality

| Aspect          | Decision                           |
| --------------- | ---------------------------------- |
| Coverage target | 90%+ comprehensive                 |
| E2E testing     | Full suite (Playwright)            |
| Pre-commit      | Full checks (lint + format + type) |
| Type checking   | Both mypy + pyright                |

## Documentation

| Aspect     | Decision       |
| ---------- | -------------- |
| Level      | Full docs site |
| Changelog  | None           |
| Versioning | SemVer         |
| License    | MIT            |

## Security

| Aspect         | Decision                             |
| -------------- | ------------------------------------ |
| Token handling | Read Claude's file directly          |
| Network        | HTTPS + cert pinning + proxy support |
| Auto-update    | Check only (notify new version)      |

## Edge Cases

| Aspect         | Decision                              |
| -------------- | ------------------------------------- |
| No network     | Offline mode UI                       |
| API down       | Status check + backoff + cached data  |
| Multi-instance | Single instance only                  |
| Rate limit     | All strategies (reduce + wait + warn) |

## Special Features

| Aspect     | Decision                              |
| ---------- | ------------------------------------- |
| Extra info | All metrics (5h, 7d, extra usage)     |
| Focus mode | DND when high + scheduled quiet hours |
| Goals      | Daily budget + pace indicator         |
| Languages  | English + Vietnamese                  |

## UI Components

| Aspect           | Decision                                 |
| ---------------- | ---------------------------------------- |
| Progress bar     | User choice (linear/circular/gauge)      |
| Countdown        | Both formats (HH:MM:SS + human readable) |
| Dashboard layout | User customizable (drag-drop)            |
| Settings UI      | Tabs in main window                      |

## Platform-Specific

| Platform | Features                         |
| -------- | -------------------------------- |
| macOS    | Menu bar app + Touch Bar support |
| Windows  | Standard app                     |
| Linux    | Standard app                     |

## Development

| Aspect          | Decision           |
| --------------- | ------------------ |
| Repo structure  | Mono-repo          |
| Branch strategy | main only          |
| PR review       | No review required |

## Performance

| Aspect  | Target       |
| ------- | ------------ |
| Memory  | < 200MB      |
| Startup | < 5s         |
| Battery | Not priority |
| Bundle  | < 100MB      |

## Release

| Aspect    | Decision                    |
| --------- | --------------------------- |
| MVP scope | Full features               |
| Timeline  | No deadline (quality first) |

---

## Key Changes from Original Plan

1. **Nuitka instead of PyInstaller** - Requires C compiler, faster binary
2. **90%+ test coverage** - High quality bar
3. **Full E2E suite** - Playwright for GUI testing
4. **Both mypy + pyright** - Strict type checking
5. **User customizable UI** - Drag-drop dashboard, configurable progress bar
6. **Focus mode + Goals** - Additional features not in original plan
7. **macOS menu bar + Touch Bar** - Platform-specific features
8. **En + Vi localization** - i18n required
9. **Full docs site** - Not just README

---

## Effort Re-estimation

| Phase          | Original | Updated | Reason                         |
| -------------- | -------- | ------- | ------------------------------ |
| 1. Backend     | 4h       | 6h      | + Focus mode, goals, i18n      |
| 2. Tauri       | 3h       | 4h      | + macOS menu bar               |
| 3. Frontend    | 5h       | 8h      | + Customizable UI, more themes |
| 4. Integration | 5h       | 6h      | + Nuitka build, cert pinning   |
| 5. Testing     | 3h       | 6h      | 90% coverage + E2E             |
| **Total**      | **20h**  | **30h** | +50% scope                     |
