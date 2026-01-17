# Tauri v2 Research Report: Features & Best Practices

**Date**: 2026-01-17 | **Project**: claudeminder

---

## 1. Project Setup: React + TypeScript + Bun

**Command**:

```bash
bun create tauri-app
# Follow prompts: React → TypeScript
# Then initialize:
cd src
bun tauri init
```

**Dev Workflow**:

```bash
bun install
bun run tauri dev  # Hot-reload both React & Rust
```

**Key Points**:

- `create-tauri-app` supports Bun as package manager (v2 native)
- Config answers: dev server `http://localhost:5173`, frontendCmd `bun run dev`
- Project structure in `docs/02-general/rules/02-tauri.md` already covers this

---

## 2. System Tray API

**Setup Pattern** (Rust):

```rust
use tauri::tray::{TrayIconBuilder, TrayIconEvent, MouseButton, MouseButtonState};
use tauri::menu::{MenuBuilder, MenuItemBuilder};

fn setup_tray(app: &tauri::App) -> Result<()> {
    let quit = MenuItemBuilder::with_id("quit", "Quit").build(app)?;
    let menu = MenuBuilder::new(app).items(&[&quit]).build()?;

    TrayIconBuilder::new()
        .menu(&menu)
        .tooltip("claudeminder: [X.X%]")  // Dynamic via frontend events
        .on_tray_icon_event(|tray, event| {
            if let TrayIconEvent::Click {
                button: MouseButton::Left,
                button_state: MouseButtonState::Up,
                ..
            } = event {
                if let Some(window) = tray.app_handle().get_webview_window("main") {
                    let _ = window.unminimize();
                    let _ = window.show();
                    let _ = window.set_focus();
                }
            }
        })
        .build(app)?;
    Ok(())
}
```

**Dynamic Updates** (Frontend):

```typescript
import { TrayIcon } from "@tauri-apps/api/tray";

// Update tooltip on usage change
await trayIcon.setTooltip(`Claude: ${utilization.toFixed(1)}%`);
await trayIcon.setIcon("icons/tray-" + Math.floor(utilization / 10) + "0.png");
```

**Supported Events**: Click, DoubleClick, Enter, Move, Leave

---

## 3. Python Sidecar Integration

**Config** (`tauri.conf.json`):

```json
{
  "bundle": {
    "externalBin": ["binaries/claudeminder-backend"]
  }
}
```

**Rust Execution** (bidirectional):

```rust
use tauri_plugin_shell::ShellExt;
use tauri_plugin_shell::process::CommandEvent;

#[tauri::command]
async fn call_backend(app: tauri::AppHandle, action: String) -> Result<String, String> {
    let (mut rx, mut child) = app
        .shell()
        .sidecar("claudeminder-backend")
        .map_err(|e| e.to_string())?
        .arg(&action)
        .spawn()
        .map_err(|e| e.to_string())?;

    let mut output = String::new();
    while let Some(event) = rx.recv().await {
        if let CommandEvent::Stdout(line) = event {
            output.push_str(&String::from_utf8_lossy(&line));
        }
    }
    Ok(output)
}
```

**Frontend Call**:

```typescript
const result = await invoke<string>("call_backend", { action: "get_usage" });
```

---

## 4. Window Management: Hide/Show/Minimize

**Hide to Tray Pattern**:

```typescript
import { getCurrentWindow } from "@tauri-apps/api/window";

const window = getCurrentWindow();
await window.hide(); // Hide to tray
await window.show(); // Restore
await window.unminimize(); // Restore from minimize
await window.set_focus(); // Focus window
```

**Tray Interaction** (already in pattern above) handles show/focus on left-click

---

## 5. Native Notifications

**Setup**:

```bash
bun add @tauri-apps/plugin-notification
```

**Rust**:

```rust
fn main() {
    tauri::Builder::default()
        .plugin(tauri_plugin_notification::init())
        .setup(|app| {
            if app.notification().permission_state()? == PermissionState::Unknown {
                app.notification().request_permission()?;
            }
            Ok(())
        })
}
```

**TypeScript**:

```typescript
import {
  isPermissionGranted,
  requestPermission,
  sendNotification,
} from "@tauri-apps/plugin-notification";

async function notifyReset() {
  let granted = await isPermissionGranted();
  if (!granted) {
    const permission = await requestPermission();
    granted = permission === "granted";
  }
  if (granted) {
    sendNotification({
      title: "Claude Token Reset",
      body: "Your 5-hour window has reset!",
    });
  }
}
```

---

## 6. Recommended Implementation Order for claudeminder

1. **Setup**: Use `create-tauri-app` with React + TypeScript + Bun
2. **Tray**: Implement `TrayIconBuilder` with tooltip updates via event emissions
3. **Window**: Hide/show with tray integration
4. **Notifications**: Plugin setup + permission handling
5. **Sidecar**: Python backend execution + JSON response parsing
6. **IPC Commands**: Thin Rust commands delegating to modules (already in rules)

---

## 7. Key Gotchas & Patterns

| Issue                  | Solution                                              |
| ---------------------- | ----------------------------------------------------- |
| Tray tooltip updates   | Use frontend `emit` → Rust listens → updates tray     |
| Sidecar exit codes     | Always check `status.success()` before parsing stdout |
| Permission requests    | Call once at startup, cache result                    |
| Window hide on startup | Use `tauri.conf.json` `visible: false`                |
| Icon scaling macOS     | Use `.icns` (1024x1024), set `iconAsTemplate: true`   |

---

## 8. Capabilities Configuration

Minimal for claudeminder (`capabilities/default.json`):

```json
{
  "permissions": [
    "core:default",
    "shell:allow-execute",
    "shell:allow-sidecar",
    "notification:default"
  ]
}
```

---

## References

- [Tauri v2 Create Project](https://v2.tauri.app/start/create-project/)
- [System Tray Documentation](https://v2.tauri.app/learn/system-tray)
- [Python Sidecar Guide](https://github.com/tauri-apps/tauri-docs/blob/v2/src/content/docs/develop/sidecar.mdx)
- [Notification Plugin](https://v2.tauri.app/plugin/notification)

---

## Unresolved Questions

None. All research areas covered. Ready for implementation planning.
