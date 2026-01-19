#[allow(unused_imports)]
use tauri::{tray::TrayIconId, AppHandle, Manager, Emitter};
use tauri::menu::{Menu, MenuItem, PredefinedMenuItem, Submenu};
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

        // Rebuild menu with updated values
        // Note: Event handlers are set via TrayIconBuilder.on_menu_event in setup.rs
        // They will be automatically preserved when menu is updated
        let menu = build_tray_menu(&app, percentage, &reset_time)
            .map_err(|e| e.to_string())?;

        tray.set_menu(Some(menu)).map_err(|e| e.to_string())?;
    }

    Ok(())
}

pub fn build_tray_menu(app: &AppHandle, percentage: u8, reset_time: &str) -> Result<Menu<tauri::Wry>, Box<dyn std::error::Error>> {
    // Usage info items (disabled, for display only)
    let usage_info = MenuItem::with_id(app, "usage_info", format!("Usage: {}%", percentage), false, None::<&str>)?;
    let reset_info = MenuItem::with_id(app, "reset_info", format!("Reset: {}", reset_time), false, None::<&str>)?;
    let separator0 = PredefinedMenuItem::separator(app)?;

    // Snooze submenu
    let snooze_5 = MenuItem::with_id(app, "snooze_5", "5 minutes", true, None::<&str>)?;
    let snooze_15 = MenuItem::with_id(app, "snooze_15", "15 minutes", true, None::<&str>)?;
    let snooze_30 = MenuItem::with_id(app, "snooze_30", "30 minutes", true, None::<&str>)?;
    let snooze_60 = MenuItem::with_id(app, "snooze_60", "1 hour", true, None::<&str>)?;
    let snooze_menu = Submenu::with_items(
        app,
        "Snooze Notifications",
        true,
        &[&snooze_5, &snooze_15, &snooze_30, &snooze_60],
    )?;

    let separator1 = PredefinedMenuItem::separator(app)?;

    // Actions
    let show = MenuItem::with_id(app, "show", "Show Window", true, None::<&str>)?;
    let overlay = MenuItem::with_id(app, "overlay", "Toggle Overlay", true, None::<&str>)?;
    let refresh = MenuItem::with_id(app, "refresh", "Refresh Now", true, None::<&str>)?;
    let settings = MenuItem::with_id(app, "settings", "Settings...", true, None::<&str>)?;

    let separator2 = PredefinedMenuItem::separator(app)?;
    let quit = MenuItem::with_id(app, "quit", "Quit", true, None::<&str>)?;

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

    Ok(menu)
}
