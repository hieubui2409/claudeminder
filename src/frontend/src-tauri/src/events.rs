use serde::{Deserialize, Serialize};

pub const EVENT_TRAY_UPDATE: &str = "tray-update";
pub const EVENT_TRAY_ANIMATE: &str = "tray-animate";
pub const EVENT_SNOOZE: &str = "snooze";

/// Payload for tray-update event
#[derive(Clone, Serialize, Deserialize, Debug)]
pub struct TrayUpdatePayload {
    pub utilization: f64,
    pub tooltip: String,
    pub color: String, // "green", "yellow", "orange", "red"
}

/// Payload for tray-animate event
#[derive(Clone, Serialize, Deserialize, Debug)]
pub struct TrayAnimatePayload {
    pub animate: bool,
}

/// Payload for snooze event
#[derive(Clone, Serialize, Deserialize, Debug)]
pub struct SnoozePayload {
    pub duration_minutes: u32,
}
