#[allow(unused_imports)]
use tauri::{tray::TrayIconId, AppHandle, Manager};
use crate::tray::dynamic_icon::generate_percentage_icon;

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

    Ok(())
}
