use crate::sidecar::backend::call_backend;
use serde::{Deserialize, Serialize};
use tauri::AppHandle;

#[derive(Debug, Serialize, Deserialize)]
pub struct FiveHourUsage {
    pub utilization: f64,
    pub resets_at: String,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct GoalsStatus {
    pub enabled: bool,
    pub is_on_track: bool,
    pub current_usage: f64,
    pub expected_usage: f64,
    pub message: String,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct FocusModeStatus {
    pub is_snoozed: bool,
    pub snooze_remaining: i64,
    pub is_quiet_hours: bool,
    pub is_dnd: bool,
    pub notifications_suppressed: bool,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct UsageResponse {
    pub five_hour: Option<FiveHourUsage>,
    pub goals: Option<GoalsStatus>,
    pub focus_mode: Option<FocusModeStatus>,
    pub error: Option<String>,
}

#[tauri::command]
pub async fn get_usage(app: AppHandle) -> Result<UsageResponse, String> {
    let output = call_backend(&app, "get_usage", &[]).await?;
    serde_json::from_str(&output).map_err(|e| e.to_string())
}

#[tauri::command]
pub async fn refresh_usage(app: AppHandle) -> Result<UsageResponse, String> {
    let output = call_backend(&app, "refresh_usage", &[]).await?;
    serde_json::from_str(&output).map_err(|e| e.to_string())
}

#[tauri::command]
pub async fn snooze(app: AppHandle, minutes: i32) -> Result<serde_json::Value, String> {
    let output = call_backend(&app, "snooze", &[&minutes.to_string()]).await?;
    serde_json::from_str(&output).map_err(|e| e.to_string())
}

#[tauri::command]
pub async fn get_config(app: AppHandle) -> Result<serde_json::Value, String> {
    let output = call_backend(&app, "get_config", &[]).await?;
    serde_json::from_str(&output).map_err(|e| e.to_string())
}

#[tauri::command]
pub async fn set_config(app: AppHandle, config_json: String) -> Result<serde_json::Value, String> {
    let output = call_backend(&app, "set_config", &[&config_json]).await?;
    serde_json::from_str(&output).map_err(|e| e.to_string())
}

#[tauri::command]
pub async fn check_reminders(
    app: AppHandle,
    usage_percent: f64,
    reset_time: Option<String>,
) -> Result<serde_json::Value, String> {
    let args: Vec<String> = match reset_time {
        Some(time) => vec![usage_percent.to_string(), time],
        None => vec![usage_percent.to_string()],
    };
    let arg_refs: Vec<&str> = args.iter().map(|s| s.as_str()).collect();
    let output = call_backend(&app, "check_reminders", &arg_refs).await?;
    serde_json::from_str(&output).map_err(|e| e.to_string())
}
