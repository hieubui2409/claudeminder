use tauri::{AppHandle, Manager};

#[tauri::command]
pub async fn toggle_overlay(app: AppHandle) -> Result<bool, String> {
    let overlay = app.get_webview_window("overlay")
        .ok_or("Overlay window not found")?;

    let is_visible = overlay.is_visible().map_err(|e| e.to_string())?;

    if is_visible {
        overlay.hide().map_err(|e| e.to_string())?;
    } else {
        overlay.show().map_err(|e| e.to_string())?;
    }

    Ok(!is_visible)
}

#[tauri::command]
pub async fn set_overlay_visible(app: AppHandle, visible: bool) -> Result<(), String> {
    let overlay = app.get_webview_window("overlay")
        .ok_or("Overlay window not found")?;

    if visible {
        overlay.show().map_err(|e| e.to_string())?;
    } else {
        overlay.hide().map_err(|e| e.to_string())?;
    }

    Ok(())
}

#[tauri::command]
pub async fn set_overlay_position(app: AppHandle, x: i32, y: i32) -> Result<(), String> {
    let overlay = app.get_webview_window("overlay")
        .ok_or("Overlay window not found")?;

    overlay.set_position(tauri::Position::Physical(tauri::PhysicalPosition { x, y }))
        .map_err(|e| e.to_string())?;

    Ok(())
}
