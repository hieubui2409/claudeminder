use tauri::{
    menu::{Menu, MenuItem, PredefinedMenuItem, Submenu},
    tray::{MouseButton, MouseButtonState, TrayIconBuilder, TrayIconEvent, TrayIconId},
    App, Emitter, Manager,
};

pub fn setup_tray(app: &App) -> Result<TrayIconId, Box<dyn std::error::Error>> {
    // Usage info items (disabled, for display only)
    let usage_info = MenuItem::with_id(app, "usage_info", "Usage: ---%", false, None::<&str>)?;
    let reset_info = MenuItem::with_id(app, "reset_info", "Reset: --:--", false, None::<&str>)?;
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

    let tray = TrayIconBuilder::with_id("main")
        .icon(app.default_window_icon().unwrap().clone())
        .menu(&menu)
        .tooltip("Claudeminder: Loading...")
        .show_menu_on_left_click(false)
        .on_menu_event(|app, event| {
            let id = event.id().as_ref();
            match id {
                "quit" => app.exit(0),
                "show" | "settings" => {
                    if let Some(window) = app.get_webview_window("main") {
                        let _ = window.show();
                        let _ = window.set_focus();
                        if id == "settings" {
                            let _ = app.emit("open-settings", ());
                        }
                    }
                }
                "refresh" => {
                    let _ = app.emit("refresh-usage", ());
                }
                "overlay" => {
                    if let Some(overlay_window) = app.get_webview_window("overlay") {
                        if overlay_window.is_visible().unwrap_or(false) {
                            let _ = overlay_window.hide();
                        } else {
                            let _ = overlay_window.show();
                        }
                    }
                }
                id if id.starts_with("snooze_") => {
                    if let Some(minutes_str) = id.strip_prefix("snooze_") {
                        if let Ok(minutes) = minutes_str.parse::<u32>() {
                            let _ = app.emit("snooze-activated", serde_json::json!({ "minutes": minutes }));
                        }
                    }
                }
                _ => {}
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

    Ok(tray.id().clone())
}
