import {
  isPermissionGranted,
  requestPermission,
  sendNotification,
} from "@tauri-apps/plugin-notification";
import { emit } from "@tauri-apps/api/event";
import { animateTray } from "./tray";

/**
 * Minimum interval between notifications (1 minute)
 */
export const NOTIFICATION_THROTTLE_MS = 60000;

/**
 * Track last notification timestamp for throttling
 */
let lastNotificationTime = 0;

/**
 * Ensure notification permission is granted
 *
 * @returns true if permission is granted, false otherwise
 */
export async function ensureNotificationPermission(): Promise<boolean> {
  try {
    let permissionGranted = await isPermissionGranted();

    if (!permissionGranted) {
      const permission = await requestPermission();
      permissionGranted = permission === "granted";
    }

    return permissionGranted;
  } catch (error) {
    console.error("Failed to check/request notification permission:", error);
    return false;
  }
}

/**
 * Check if notifications can be sent (throttle + permission check)
 *
 * @returns true if notification can be sent
 */
export function canNotify(): boolean {
  const now = Date.now();
  const timeSinceLastNotification = now - lastNotificationTime;

  return timeSinceLastNotification >= NOTIFICATION_THROTTLE_MS;
}

/**
 * Send a reminder notification
 *
 * @param title - Notification title
 * @param body - Notification body
 */
export async function notifyReminder(
  title: string,
  body: string,
): Promise<void> {
  try {
    if (!canNotify()) {
      console.debug("Notification throttled");
      return;
    }

    const hasPermission = await ensureNotificationPermission();
    if (!hasPermission) {
      console.warn("Notification permission not granted");
      return;
    }

    await sendNotification({ title, body });
    lastNotificationTime = Date.now();

    // Animate tray to draw attention
    await animateTray(1500);
  } catch (error) {
    console.error("Failed to send reminder notification:", error);
    throw error;
  }
}

/**
 * Send usage warning notification based on percentage
 *
 * @param percentage - Current usage percentage (0-100)
 */
export async function notifyUsageWarning(percentage: number): Promise<void> {
  try {
    if (percentage >= 90) {
      await notifyReminder(
        "Critical Usage Alert",
        `You've used ${percentage.toFixed(1)}% of your Claude quota. Consider saving your work.`,
      );
    } else if (percentage >= 75) {
      await notifyReminder(
        "High Usage Warning",
        `You've used ${percentage.toFixed(1)}% of your Claude quota.`,
      );
    }
  } catch (error) {
    console.error("Failed to send usage warning:", error);
  }
}

/**
 * Send reset soon notification
 *
 * @param minutes - Minutes until reset
 */
export async function notifyResetSoon(minutes: number): Promise<void> {
  try {
    const timeStr =
      minutes < 60
        ? `${minutes} minute${minutes !== 1 ? "s" : ""}`
        : `${Math.floor(minutes / 60)} hour${Math.floor(minutes / 60) !== 1 ? "s" : ""}`;

    await notifyReminder(
      "Reset Soon",
      `Your Claude usage quota will reset in ${timeStr}.`,
    );
  } catch (error) {
    console.error("Failed to send reset soon notification:", error);
  }
}

/**
 * Send token expired notification
 */
export async function notifyTokenExpired(): Promise<void> {
  try {
    await notifyReminder(
      "Token Expired",
      "Your Claude authentication token has expired. Please log in again.",
    );
  } catch (error) {
    console.error("Failed to send token expired notification:", error);
  }
}

/**
 * Send offline/network error notification
 */
export async function notifyOffline(): Promise<void> {
  try {
    await notifyReminder(
      "Network Error",
      "Unable to connect to Claude API. Please check your internet connection.",
    );
  } catch (error) {
    console.error("Failed to send offline notification:", error);
  }
}

/**
 * Send rate limited notification
 */
export async function notifyRateLimited(): Promise<void> {
  try {
    await notifyReminder(
      "Rate Limited",
      "Claude API rate limit reached. Please wait before retrying.",
    );
  } catch (error) {
    console.error("Failed to send rate limited notification:", error);
  }
}

/**
 * Handle snooze request
 *
 * @param minutes - Duration to snooze notifications (in minutes)
 */
export async function handleSnooze(minutes: number): Promise<void> {
  try {
    await emit("snooze", { duration_minutes: minutes });
    console.log(`Notifications snoozed for ${minutes} minutes`);
  } catch (error) {
    console.error("Failed to handle snooze:", error);
    throw error;
  }
}
