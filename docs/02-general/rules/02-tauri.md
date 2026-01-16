# Tauri v2 Rules

SCOPE: `src/frontend/src-tauri/**/*.rs`, `src/frontend/src/**/*.{ts,tsx}`
TOOLS: Tauri v2, Rust, TypeScript, React

---

## Project Structure

```
src/frontend/
├── src/                    # React frontend
│   ├── components/         # UI components
│   ├── hooks/              # Custom React hooks
│   ├── stores/             # State management
│   ├── styles/             # CSS/theme files
│   ├── types/              # TypeScript types
│   └── utils/              # Utility functions
├── src-tauri/              # Rust backend
│   ├── src/
│   │   ├── main.rs         # Entry point
│   │   ├── lib.rs          # Library exports
│   │   ├── commands/       # IPC commands
│   │   ├── tray/           # System tray logic
│   │   └── sidecar/        # Python sidecar integration
│   ├── Cargo.toml
│   ├── tauri.conf.json
│   └── capabilities/       # Permission capabilities
└── package.json
```

---

## Tauri Commands (IPC)

ALWAYS:

- Use `#[tauri::command]` for frontend-callable functions
- Return `Result<T, String>` for error handling
- Keep commands thin - delegate to modules
- Use `tauri::State` for shared state

PATTERN:

```rust
#[tauri::command]
async fn get_usage(
    app: tauri::AppHandle,
    state: tauri::State<'_, AppState>,
) -> Result<UsageResponse, String> {
    state.usage_tracker.get_current()
        .await
        .map_err(|e| e.to_string())
}
```

---

## System Tray (v2)

ALWAYS:

- Use `TrayIconBuilder` for creating tray
- Handle both left-click and right-click events
- Update icon dynamically based on usage percentage
- Use `on_tray_icon_event` for mouse events

PATTERN:

```rust
use tauri::tray::{TrayIconBuilder, TrayIconEvent, MouseButton, MouseButtonState};
use tauri::menu::{Menu, MenuItem};

fn setup_tray(app: &tauri::App) -> Result<(), Box<dyn std::error::Error>> {
    let quit = MenuItem::with_id(app, "quit", "Quit", true, None::<&str>)?;
    let menu = Menu::with_items(app, &[&quit])?;

    TrayIconBuilder::new()
        .icon(app.default_window_icon().unwrap().clone())
        .menu(&menu)
        .tooltip("claudiminder")
        .on_menu_event(|app, event| {
            if event.id().as_ref() == "quit" {
                app.exit(0);
            }
        })
        .on_tray_icon_event(|tray, event| {
            if let TrayIconEvent::Click {
                button: MouseButton::Left,
                button_state: MouseButtonState::Up,
                ..
            } = event
            {
                if let Some(window) = tray.app_handle().get_webview_window("main") {
                    let _ = window.show();
                    let _ = window.set_focus();
                }
            }
        })
        .build(app)?;

    Ok(())
}
```

---

## Python Sidecar

ALWAYS:

- Configure sidecar in `tauri.conf.json` under `bundle.externalBin`
- Use `tauri_plugin_shell::ShellExt` for execution
- Handle stdout/stderr asynchronously
- Parse JSON responses from Python

PATTERN:

```rust
use tauri_plugin_shell::ShellExt;

#[tauri::command]
async fn call_backend(app: tauri::AppHandle, action: String) -> Result<String, String> {
    let output = app
        .shell()
        .sidecar("claudiminder-backend")
        .map_err(|e| e.to_string())?
        .arg(&action)
        .output()
        .await
        .map_err(|e| e.to_string())?;

    if output.status.success() {
        Ok(String::from_utf8_lossy(&output.stdout).to_string())
    } else {
        Err(String::from_utf8_lossy(&output.stderr).to_string())
    }
}
```

---

## Frontend (React + TypeScript)

ALWAYS:

- Use `@tauri-apps/api` for IPC calls
- Use `invoke` for command calls
- Handle errors gracefully with try/catch
- Use TypeScript strict mode

PATTERN:

```typescript
import { invoke } from "@tauri-apps/api/core";

interface UsageResponse {
  utilization: number;
  resets_at: string;
}

async function fetchUsage(): Promise<UsageResponse> {
  return await invoke<UsageResponse>("get_usage");
}
```

---

## Capabilities & Permissions

ALWAYS:

- Define minimal permissions in `capabilities/`
- Use capability files for sidecar permissions
- Never grant unnecessary file system access

PATTERN (`capabilities/default.json`):

```json
{
  "$schema": "../gen/schemas/desktop-schema.json",
  "identifier": "default",
  "description": "Default capabilities for claudiminder",
  "windows": ["main"],
  "permissions": ["core:default", "shell:allow-execute", "shell:allow-sidecar"]
}
```

---

## Configuration (`tauri.conf.json`)

KEY SETTINGS:

```json
{
  "productName": "claudiminder",
  "identifier": "com.claudiminder.app",
  "bundle": {
    "active": true,
    "targets": "all",
    "externalBin": ["binaries/claudiminder-backend"],
    "icon": ["icons/icon.png"]
  },
  "app": {
    "trayIcon": {
      "iconPath": "icons/tray.png",
      "iconAsTemplate": true
    }
  }
}
```

---

## Themes & Styling

SUPPORTED THEMES:

1. Light / Dark (standard)
2. Neon Light / Neon Dark (vibrant)
3. Glassmorphism Light / Dark (frosted glass effect)

ALWAYS:

- Use CSS custom properties for theming
- Support system preference detection
- Persist user preference in config
- Use smooth transitions between themes

---

## Error Handling

ALWAYS:

- Rust: Return `Result<T, String>` from commands
- TypeScript: Use try/catch with typed errors
- Show user-friendly error messages in UI
- Log technical details for debugging

NEVER:

- Panic in production code
- Swallow errors silently
- Expose internal error details to users
