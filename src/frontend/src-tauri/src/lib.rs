mod commands;
mod events;
mod sidecar;
mod tray;

use tauri::{Listener, Manager};

#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
    let builder = tauri::Builder::default()
        .plugin(tauri_plugin_shell::init())
        .plugin(tauri_plugin_notification::init())
        .plugin(tauri_plugin_single_instance::init(|app, _args, _cwd| {
            if let Some(window) = app.get_webview_window("main") {
                let _ = window.show();
                let _ = window.set_focus();
            }
        }));

    builder
        .setup(|app| {
            let tray_id = tray::setup::setup_tray(app)?;

            // Setup window close -> hide behavior
            if let Some(window) = app.get_webview_window("main") {
                let window_clone = window.clone();
                window.on_window_event(move |event| {
                    if let tauri::WindowEvent::CloseRequested { api, .. } = event {
                        api.prevent_close();
                        let _ = window_clone.hide();
                    }
                });
            }

            // Setup event listeners
            let app_handle = app.handle().clone();
            let tray_id_clone = tray_id.clone();
            app.listen(events::EVENT_TRAY_UPDATE, move |event: tauri::Event| {
                let payload = event.payload();
                if let Ok(data) = serde_json::from_str::<events::TrayUpdatePayload>(payload) {
                    if let Some(tray) = app_handle.tray_by_id(&tray_id_clone) {
                        let _ = tray.set_tooltip(Some(&data.tooltip));
                    }
                }
            });

            let app_handle = app.handle().clone();
            app.listen(events::EVENT_TRAY_ANIMATE, move |event: tauri::Event| {
                let payload = event.payload();
                if let Ok(_data) = serde_json::from_str::<events::TrayAnimatePayload>(payload) {
                    let _ = &app_handle;
                }
            });

            let app_handle = app.handle().clone();
            app.listen(events::EVENT_SNOOZE, move |event: tauri::Event| {
                let payload = event.payload();
                if let Ok(_data) = serde_json::from_str::<events::SnoozePayload>(payload) {
                    let _ = &app_handle;
                }
            });

            // Request notification permission (sync in this version)
            #[cfg(desktop)]
            {
                let handle = app.handle().clone();
                let _ = tauri_plugin_notification::NotificationExt::notification(&handle)
                    .request_permission();
            }

            Ok(())
        })
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
            tray::commands::update_tray_info,
        ])
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
