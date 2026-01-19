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
