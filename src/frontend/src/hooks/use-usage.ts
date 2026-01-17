import { invoke } from "@tauri-apps/api/core";
import { useCallback, useEffect, useRef, useState } from "react";
import type { UsageResponse } from "../types/usage";
import { updateTray } from "../utils/tray";
import {
  notifyUsageWarning,
  notifyOffline,
  notifyRateLimited,
} from "../utils/notifications";
import { handleTokenExpired } from "../utils/token-refresh";
import { isTauri, getMockUsageData } from "../utils/mock-data";

export function useUsage(pollInterval = 60000) {
  const [usage, setUsage] = useState<UsageResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [isOffline, setIsOffline] = useState(false);
  const [isRateLimited, setIsRateLimited] = useState(false);

  const lastPercentageRef = useRef<number | null>(null);

  const fetchUsage = useCallback(async () => {
    try {
      setLoading(true);

      // Use mock data when not in Tauri (browser mode)
      const result = isTauri()
        ? await invoke<UsageResponse>("get_usage")
        : getMockUsageData();

      // Check for error states
      if (result.token_expired) {
        await handleTokenExpired();
        setError("Token expired. Please re-login.");
        return;
      }

      if (result.rate_limited) {
        setIsRateLimited(true);
        await notifyRateLimited();
        setError("Rate limit exceeded");
        return;
      }

      if (result.offline) {
        setIsOffline(true);
        await notifyOffline();
        setError("Network error");
        return;
      }

      // Success - clear error states
      setIsRateLimited(false);
      setIsOffline(false);
      setUsage(result);
      setError(result.error || null);

      // Update tray and check notifications
      if (result.five_hour) {
        const { utilization, resets_at } = result.five_hour;
        // API returns utilization as percentage (0-100)
        const percentage = utilization;

        // Update tray with percentage
        await updateTray(percentage, resets_at);

        // Check for usage warnings (only on increase)
        if (
          lastPercentageRef.current !== null &&
          percentage > lastPercentageRef.current
        ) {
          await notifyUsageWarning(percentage);
        }
        lastPercentageRef.current = percentage;
      }
    } catch (e: unknown) {
      const errorMessage = e instanceof Error ? e.message : String(e);

      // Check if it's a network error
      if (
        errorMessage.toLowerCase().includes("network") ||
        errorMessage.toLowerCase().includes("connection")
      ) {
        setIsOffline(true);
        await notifyOffline();
      }

      setError(errorMessage);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchUsage();
    const interval = setInterval(fetchUsage, pollInterval);
    return () => clearInterval(interval);
  }, [fetchUsage, pollInterval]);

  return {
    usage,
    loading,
    error,
    isOffline,
    isRateLimited,
    refresh: fetchUsage,
  };
}
