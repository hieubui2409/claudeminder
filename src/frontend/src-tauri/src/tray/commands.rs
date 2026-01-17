#[allow(unused_imports)]
use tauri::{tray::TrayIconId, AppHandle, Manager};

#[tauri::command]
pub fn update_tray_info(
    app: AppHandle,
    tooltip: String,
) -> Result<(), String> {
    let tray_id: TrayIconId = "main".into();

    // Update tooltip
    if let Some(tray) = app.tray_by_id(&tray_id) {
        tray.set_tooltip(Some(&tooltip)).map_err(|e| e.to_string())?;
    }

    Ok(())
}
