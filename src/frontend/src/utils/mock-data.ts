import type { UsageResponse } from "../types/usage";

// Check if running in Tauri environment
export function isTauri(): boolean {
  return typeof window !== "undefined" && "__TAURI_INTERNALS__" in window;
}

// Generate mock usage data for browser testing
export function getMockUsageData(): UsageResponse {
  const now = new Date();
  const resetTime = new Date(now.getTime() + 2 * 60 * 60 * 1000); // 2 hours from now

  return {
    five_hour: {
      utilization: 42, // 42% usage (API returns percentage directly)
      resets_at: resetTime.toISOString(),
      input_tokens_used: 420000,
      input_tokens_limit: 1000000,
      output_tokens_used: 84000,
      output_tokens_limit: 200000,
    },
    goals: {
      enabled: true,
      is_on_track: true,
      current_usage: 420000,
      expected_usage: 500000,
      message: "On track",
    },
    focus_mode: {
      is_snoozed: false,
      snooze_remaining: 0,
      is_quiet_hours: false,
      is_dnd: false,
      notifications_suppressed: false,
    },
  };
}
