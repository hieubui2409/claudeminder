# Phase 2: Tauri Backend

## Context Links

- [Main Plan](./plan.md)
- [lib.rs](../../src/frontend/src-tauri/src/lib.rs)
- [commands/mod.rs](../../src/frontend/src-tauri/src/commands/mod.rs)
- [commands/overlay.rs](../../src/frontend/src-tauri/src/commands/overlay.rs)
- [tray/setup.rs](../../src/frontend/src-tauri/src/tray/setup.rs)
- [tauri.conf.json](../../src/frontend/src-tauri/tauri.conf.json)

## Parallelization Info

| Property       | Value                       |
| -------------- | --------------------------- |
| Can run with   | Phase 1 (Frontend Settings) |
| Blocked by     | None                        |
| Blocks         | Phase 3 (Integration)       |
| Estimated time | 2 hours                     |

## Overview

- **Priority**: P2
- **Status**: completed
- **Description**: Add Tauri commands for window visibility, dynamic tray icon with %, tray menu with usage info

## Key Insights

- Current lib.rs setup hides main window on close (prevent_close + hide)
- Overlay window starts hidden (visible=false in tauri.conf.json)
- Main window starts visible (visible=true in tauri.conf.json)
- Tray already has update_tray_info command for tooltip updates
- Need to generate icon dynamically with % text overlay
- Tray menu needs usage info items (non-clickable)

## Requirements

### Functional

- FR1: Command to apply show mode settings on app ready
- FR2: Support "main", "overlay", "both" modes
- FR3: Dynamic tray icon showing usage percentage
- FR4: Tray menu displays usage % and reset time
- FR5: Save/restore overlay position

### Non-Functional

- NFR1: Commands must be async for Tauri v2 compatibility
- NFR2: Handle window not found gracefully
- NFR3: Icon generation should be fast (cache when possible)
- NFR4: No blocking operations in setup

## Architecture

### Command Flow

```
┌─────────────────────────────────┐
│         Frontend                │
│  (reads localStorage settings)  │
└─────────────┬───────────────────┘
              │ invoke("apply_show_mode", { mode })
              ▼
┌─────────────────────────────────┐
│      Tauri Commands             │
│    - apply_show_mode            │
│    - save_overlay_position      │
│    - get_overlay_position       │
│    - update_tray_with_usage     │
└─────────────────────────────────┘
```

### Dynamic Icon Flow

```
Usage Update Event
       │
       ▼
┌────────────────────┐
│ generate_tray_icon │
│ (% text overlay)   │
└─────────┬──────────┘
          │
          ▼
┌────────────────────┐
│ tray.set_icon()    │
└────────────────────┘
```

### Tray Menu Structure

```
┌─────────────────────────┐
│ Usage: 45%              │  (disabled, info only)
│ Reset: 2h 30m           │  (disabled, info only)
├─────────────────────────┤
│ Snooze Notifications ►  │
├─────────────────────────┤
│ Show Window             │
│ Toggle Overlay          │
│ Refresh Now             │
│ Settings...             │
├─────────────────────────┤
│ Quit                    │
└─────────────────────────┘
```

## Related Code Files

### To Modify

| File                            | Changes                             |
| ------------------------------- | ----------------------------------- |
| `src-tauri/src/lib.rs`          | Register new commands               |
| `src-tauri/src/commands/mod.rs` | Export window module                |
| `src-tauri/src/tray/setup.rs`   | Add usage info menu items           |
| `src-tauri/src/tray/mod.rs`     | Export dynamic_icon module          |
| `src-tauri/Cargo.toml`          | Add image crate for icon generation |

### To Create

| File                                 | Purpose                        |
| ------------------------------------ | ------------------------------ |
| `src-tauri/src/commands/window.rs`   | Window visibility commands     |
| `src-tauri/src/tray/dynamic_icon.rs` | Generate tray icon with % text |

## File Ownership

**CRITICAL**: This phase ONLY modifies Tauri/Rust files. Do NOT touch:

- Any files in `src/frontend/src/` (Phase 1)
- `App.tsx`, `Overlay.tsx`, `main.tsx` (Phase 3)

## Implementation Steps

### Step 1: Add Dependencies (Cargo.toml)

Add image crate for icon generation:

```toml
[dependencies]
image = "0.25"
```

### Step 2: Create window.rs Commands

Location: `src/frontend/src-tauri/src/commands/window.rs`

```rust
use tauri::{AppHandle, Manager};
use serde::{Deserialize, Serialize};

#[derive(Debug, Serialize, Deserialize)]
pub struct OverlayPosition {
    pub x: i32,
    pub y: i32,
}

#[tauri::command]
pub async fn apply_show_mode(app: AppHandle, mode: String) -> Result<(), String> {
    let main = app.get_webview_window("main");
    let overlay = app.get_webview_window("overlay");

    match mode.as_str() {
        "main" => {
            if let Some(w) = main {
                w.show().map_err(|e| e.to_string())?;
            }
            if let Some(w) = overlay {
                w.hide().map_err(|e| e.to_string())?;
            }
        }
        "overlay" => {
            if let Some(w) = main {
                w.hide().map_err(|e| e.to_string())?;
            }
            if let Some(w) = overlay {
                w.show().map_err(|e| e.to_string())?;
            }
        }
        "both" => {
            if let Some(w) = main {
                w.show().map_err(|e| e.to_string())?;
            }
            if let Some(w) = overlay {
                w.show().map_err(|e| e.to_string())?;
            }
        }
        _ => return Err(format!("Invalid show mode: {}", mode)),
    }

    Ok(())
}

#[tauri::command]
pub async fn save_overlay_position(app: AppHandle, position: OverlayPosition) -> Result<(), String> {
    if let Some(overlay) = app.get_webview_window("overlay") {
        overlay.set_position(tauri::Position::Physical(tauri::PhysicalPosition {
            x: position.x,
            y: position.y,
        })).map_err(|e| e.to_string())?;
    }
    Ok(())
}

#[tauri::command]
pub async fn get_overlay_position(app: AppHandle) -> Result<OverlayPosition, String> {
    let overlay = app.get_webview_window("overlay")
        .ok_or("Overlay window not found")?;

    let pos = overlay.outer_position().map_err(|e| e.to_string())?;
    Ok(OverlayPosition {
        x: pos.x,
        y: pos.y,
    })
}
```

### Step 3: Create dynamic_icon.rs

Location: `src/frontend/src-tauri/src/tray/dynamic_icon.rs`

```rust
use image::{Rgba, RgbaImage};
use tauri::image::Image;

/// Generate a tray icon with usage percentage text overlay
pub fn generate_percentage_icon(percentage: u8) -> Image<'static> {
    let size = 22u32; // Standard tray icon size
    let mut img = RgbaImage::new(size, size);

    // Background color based on usage level
    let bg_color = if percentage > 80 {
        Rgba([220, 53, 69, 255])   // Red
    } else if percentage > 60 {
        Rgba([255, 193, 7, 255])   // Yellow
    } else {
        Rgba([40, 167, 69, 255])   // Green
    };

    // Fill background circle
    let center = (size / 2) as f32;
    let radius = (size / 2 - 1) as f32;

    for y in 0..size {
        for x in 0..size {
            let dx = x as f32 - center;
            let dy = y as f32 - center;
            if dx * dx + dy * dy <= radius * radius {
                img.put_pixel(x, y, bg_color);
            }
        }
    }

    // Draw percentage text (simplified - just show number)
    // For production, consider using a font rendering library
    let text = if percentage >= 100 { "!".to_string() } else { format!("{}", percentage) };
    draw_text_centered(&mut img, &text, size);

    let pixels = img.into_raw();
    Image::new_owned(pixels, size, size)
}

fn draw_text_centered(img: &mut RgbaImage, text: &str, size: u32) {
    let white = Rgba([255, 255, 255, 255]);
    let center_x = size / 2;
    let center_y = size / 2;

    // Simple bitmap font for digits (3x5 pixels each)
    let digits: [[[u8; 3]; 5]; 11] = [
        // 0
        [[1,1,1], [1,0,1], [1,0,1], [1,0,1], [1,1,1]],
        // 1
        [[0,1,0], [1,1,0], [0,1,0], [0,1,0], [1,1,1]],
        // 2
        [[1,1,1], [0,0,1], [1,1,1], [1,0,0], [1,1,1]],
        // 3
        [[1,1,1], [0,0,1], [1,1,1], [0,0,1], [1,1,1]],
        // 4
        [[1,0,1], [1,0,1], [1,1,1], [0,0,1], [0,0,1]],
        // 5
        [[1,1,1], [1,0,0], [1,1,1], [0,0,1], [1,1,1]],
        // 6
        [[1,1,1], [1,0,0], [1,1,1], [1,0,1], [1,1,1]],
        // 7
        [[1,1,1], [0,0,1], [0,0,1], [0,0,1], [0,0,1]],
        // 8
        [[1,1,1], [1,0,1], [1,1,1], [1,0,1], [1,1,1]],
        // 9
        [[1,1,1], [1,0,1], [1,1,1], [0,0,1], [1,1,1]],
        // ! (exclamation for 100%)
        [[0,1,0], [0,1,0], [0,1,0], [0,0,0], [0,1,0]],
    ];

    let char_width = 3;
    let char_height = 5;
    let spacing = 1;

    let total_width = text.len() as u32 * (char_width + spacing) - spacing;
    let start_x = center_x.saturating_sub(total_width / 2);
    let start_y = center_y.saturating_sub(char_height / 2);

    for (i, c) in text.chars().enumerate() {
        let digit_idx = match c {
            '0'..='9' => c as usize - '0' as usize,
            '!' => 10,
            _ => continue,
        };

        let offset_x = start_x + i as u32 * (char_width + spacing);

        for (row, line) in digits[digit_idx].iter().enumerate() {
            for (col, &pixel) in line.iter().enumerate() {
                if pixel == 1 {
                    let px = offset_x + col as u32;
                    let py = start_y + row as u32;
                    if px < size && py < size {
                        img.put_pixel(px, py, white);
                    }
                }
            }
        }
    }
}
```

### Step 4: Update tray/mod.rs

Add export:

```rust
pub mod commands;
pub mod setup;
pub mod dynamic_icon;
```

### Step 5: Update tray/setup.rs

Add usage info menu items at top:

```rust
use crate::tray::dynamic_icon::generate_percentage_icon;

pub fn setup_tray(app: &App) -> Result<TrayIconId, Box<dyn std::error::Error>> {
    // Usage info items (disabled, for display only)
    let usage_info = MenuItem::with_id(app, "usage_info", "Usage: ---%", false, None::<&str>)?;
    let reset_info = MenuItem::with_id(app, "reset_info", "Reset: --:--", false, None::<&str>)?;
    let separator0 = PredefinedMenuItem::separator(app)?;

    // Snooze submenu (existing)
    // ...

    let menu = Menu::with_items(
        app,
        &[
            &usage_info,
            &reset_info,
            &separator0,
            &snooze_menu,
            &separator1,
            &show,
            &overlay,
            &refresh,
            &settings,
            &separator2,
            &quit,
        ],
    )?;

    // ... rest of setup
}
```

### Step 6: Add tray update command

In `src-tauri/src/tray/commands.rs`:

```rust
use tauri::{AppHandle, Manager};
use crate::tray::dynamic_icon::generate_percentage_icon;

#[tauri::command]
pub async fn update_tray_with_usage(
    app: AppHandle,
    percentage: u8,
    reset_time: String,
) -> Result<(), String> {
    // Update tray icon
    let icon = generate_percentage_icon(percentage);
    if let Some(tray) = app.tray_by_id("main") {
        tray.set_icon(Some(icon)).map_err(|e| e.to_string())?;

        // Update tooltip
        let tooltip = format!("Claudeminder: {}% used\nReset: {}", percentage, reset_time);
        tray.set_tooltip(Some(&tooltip)).map_err(|e| e.to_string())?;
    }

    // Update menu items
    if let Some(menu) = app.menu().and_then(|m| m.get("usage_info")) {
        // Note: Menu item text update requires rebuild in Tauri v2
        // This is a known limitation - consider using tray.set_menu() with new menu
    }

    Ok(())
}
```

### Step 7: Update commands/mod.rs

```rust
pub mod overlay;
pub mod usage;
pub mod window;
```

### Step 8: Update lib.rs

Register new commands:

```rust
.invoke_handler(tauri::generate_handler![
    commands::usage::get_usage,
    commands::usage::refresh_usage,
    commands::usage::snooze,
    commands::usage::get_config,
    commands::usage::set_config,
    commands::usage::check_reminders,
    commands::overlay::toggle_overlay,
    commands::overlay::set_overlay_visible,
    commands::overlay::set_overlay_position,
    commands::window::apply_show_mode,
    commands::window::save_overlay_position,
    commands::window::get_overlay_position,
    tray::commands::update_tray_info,
    tray::commands::update_tray_with_usage,
])
```

## Todo List

- [x] Add image crate to Cargo.toml
- [x] Create src-tauri/src/commands/window.rs
- [x] Create src-tauri/src/tray/dynamic_icon.rs
- [x] Update tray/mod.rs exports
- [x] Update tray/setup.rs with usage info menu items
- [x] Add update_tray_with_usage command
- [x] Update commands/mod.rs
- [x] Register new commands in lib.rs
- [x] Test apply_show_mode with all modes (requires Phase 3)
- [x] Test dynamic icon generation (requires Phase 3)
- [x] Verify cargo build succeeds

## Success Criteria

1. `apply_show_mode("main")` shows main, hides overlay
2. `apply_show_mode("overlay")` hides main, shows overlay
3. `apply_show_mode("both")` shows both windows
4. Tray icon displays percentage with color coding
5. Tray menu shows usage info items
6. `save_overlay_position` and `get_overlay_position` work correctly
7. `cargo build` succeeds with no warnings

## Conflict Prevention

**DO NOT** modify these files (owned by other phases):

- `src/frontend/src/*` (Phase 1)
- `App.tsx`, `Overlay.tsx`, `main.tsx` (Phase 3)

**Safe to modify**:

- `src-tauri/src/commands/` - adding new module
- `src-tauri/src/tray/` - adding new module, modifying setup
- `src-tauri/src/lib.rs` - adding to invoke_handler only

## Risk Assessment

| Risk                           | Likelihood | Impact | Mitigation                                   |
| ------------------------------ | ---------- | ------ | -------------------------------------------- |
| Window not found on first call | Low        | Medium | Check window exists before operations        |
| Icon rendering performance     | Low        | Medium | Simple bitmap font, no external deps         |
| Tray menu update limitation    | Medium     | Low    | Document limitation, use tooltip as fallback |

## Security Considerations

- Commands only control window visibility (no sensitive data)
- No file system access beyond icon generation
- No user input validation needed beyond mode string

## Testing Commands

After implementation, test via Tauri dev console:

```javascript
const { invoke } = window.__TAURI__.core;

// Test show modes
await invoke("apply_show_mode", { mode: "main" });
await invoke("apply_show_mode", { mode: "overlay" });
await invoke("apply_show_mode", { mode: "both" });

// Test overlay position
await invoke("save_overlay_position", { position: { x: 100, y: 100 } });
const pos = await invoke("get_overlay_position");

// Test tray update
await invoke("update_tray_with_usage", { percentage: 45, resetTime: "2h 30m" });
```

## Next Steps

After completion:

1. Notify Phase 3 that Tauri commands are ready
2. Provide command signatures for frontend integration
3. Document icon color thresholds for design review
