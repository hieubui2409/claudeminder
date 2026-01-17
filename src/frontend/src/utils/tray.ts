import { invoke } from "@tauri-apps/api/core";
import { emit } from "@tauri-apps/api/event";
import { isTauri } from "./mock-data";

/**
 * Format reset time for tooltip display
 */
function formatResetTime(resetsAt: string): string {
  try {
    const resetDate = new Date(resetsAt);
    const now = new Date();
    const diff = resetDate.getTime() - now.getTime();

    if (diff <= 0) {
      return "Resetting soon";
    }

    const hours = Math.floor(diff / (1000 * 60 * 60));
    const minutes = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60));

    if (hours > 0) {
      return `Resets in ${hours}h ${minutes}m`;
    }
    return `Resets in ${minutes}m`;
  } catch (error) {
    console.error("Failed to format reset time:", error);
    return "Reset time unknown";
  }
}

/**
 * Update system tray with current usage information
 *
 * @param utilization - Usage percentage (0-100)
 * @param resetsAt - ISO timestamp of next reset
 */
export async function updateTray(
  utilization: number,
  resetsAt: string,
): Promise<void> {
  // Skip tray updates in browser mode
  if (!isTauri()) return;

  try {
    const resetInfo = formatResetTime(resetsAt);
    const tooltip = `Claudeminder\n━━━━━━━━━━━━━━━\nUsage: ${utilization.toFixed(1)}%\n${resetInfo}`;

    // Call Tauri command to update tray tooltip
    await invoke("update_tray_info", { tooltip });
  } catch (error) {
    console.error("Failed to update tray:", error);
  }
}

/**
 * Trigger tray icon animation (e.g., for notifications)
 *
 * @param durationMs - Animation duration in milliseconds (default: 1000ms)
 */
export async function animateTray(durationMs: number = 1000): Promise<void> {
  // Skip tray animation in browser mode
  if (!isTauri()) return;

  try {
    await emit("tray-animate", { duration: durationMs });
  } catch (error) {
    console.error("Failed to animate tray:", error);
    throw error;
  }
}
