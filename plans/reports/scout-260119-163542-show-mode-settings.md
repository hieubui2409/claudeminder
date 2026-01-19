# Scout Report: Show Mode Settings

## Task

Add show mode setting (main window, overlay, both) + check trace on close setting

## Key Files

### Frontend Settings

| File                                                     | Purpose                                                                                                   |
| -------------------------------------------------------- | --------------------------------------------------------------------------------------------------------- |
| `src/frontend/src/stores/settings-store.ts`              | Zustand store - UI settings: fontSize, progressBarType, focusMode, refreshInterval. Persists localStorage |
| `src/frontend/src/types/settings.ts`                     | TypeScript types for settings                                                                             |
| `src/frontend/src/components/settings/SettingsPanel.tsx` | Settings UI wrapper                                                                                       |

### Overlay & Window

| File                                             | Purpose                                                                         |
| ------------------------------------------------ | ------------------------------------------------------------------------------- |
| `src/frontend/src/Overlay.tsx`                   | Overlay component - usage %, reset time, calls `set_overlay_visible`            |
| `src/frontend/src-tauri/src/commands/overlay.rs` | Tauri commands: `toggle_overlay`, `set_overlay_visible`, `set_overlay_position` |
| `src/frontend/src-tauri/src/lib.rs`              | Window close→hide behavior, event listeners, tray setup                         |
| `src/frontend/src-tauri/src/tray/setup.rs`       | Tray menu: Show Window, Toggle Overlay, Refresh, Settings, Quit                 |
| `src/frontend/src-tauri/tauri.conf.json`         | Window defs: main (400x600, visible), overlay (180x80, hidden, always-on-top)   |

### Backend Config

| File                                 | Purpose                                        |
| ------------------------------------ | ---------------------------------------------- |
| `src/backend/core/config_manager.py` | TOML config at `~/.config/backend/config.toml` |
| `src/backend/models/settings.py`     | Pydantic settings, env-based                   |

## Current State

### Existing Settings

- fontSize (50-150%)
- progressBarType (linear/circular/gauge)
- focusMode toggle
- refreshInterval (30-300s)

### Window Behavior

- **Main**: visible=true on start, close→hide
- **Overlay**: visible=false on start, always-on-top, transparent
- **Tray**: left-click shows main, menu toggle overlay

### Missing Features

1. **No show mode setting** - can't choose main/overlay/both on startup
2. **No trace-on-close setting** - no setting to enable/disable background tracking when windows closed

## Unresolved Questions

1. Should show mode affect startup only or also app behavior during session?
2. Should "trace when closed" stop all backend polling or just hide notifications?
