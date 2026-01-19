import { useEffect, useRef, useState } from "react";
import { invoke } from "@tauri-apps/api/core";
import { listen } from "@tauri-apps/api/event";
import { useTranslation } from "react-i18next";
import { isTauri } from "./utils/mock-data";
import { motion } from "framer-motion";

import { useUsage } from "./hooks/use-usage";
import { useTheme } from "./hooks/use-theme";
import { useSettingsStore } from "./stores/settings-store";

import { GlassCard } from "./components/ui";
import { CircularProgress, ResetCountdown } from "./components/dashboard";
import { SettingsPanel, FocusModeToggle } from "./components/settings";

import {
  notifyResetSoon,
  ensureNotificationPermission,
} from "./utils/notifications";

import "./i18n";
import "./styles/index.css";
import styles from "./App.module.css";

const REMINDER_MINUTES = [30, 15, 5];

function App() {
  const { t } = useTranslation();
  const { fontSize, refreshInterval } = useSettingsStore();
  const { usage, loading, error, isOffline, isRateLimited, refresh } = useUsage(
    refreshInterval * 1000,
  ); // Convert seconds to milliseconds
  const { theme, applyTheme } = useTheme();
  const [focusMode, setFocusMode] = useState(false);
  const [snoozeUntil, setSnoozeUntil] = useState<number | null>(null);
  const [showSettings, setShowSettings] = useState(false);
  const notifiedMinutesRef = useRef<Set<number>>(new Set());

  useEffect(() => {
    applyTheme();
  }, [theme, applyTheme]);

  useEffect(() => {
    document.documentElement.style.fontSize = `${fontSize}%`;
  }, [fontSize]);

  useEffect(() => {
    ensureNotificationPermission();
  }, []);

  // Apply show mode on startup
  useEffect(() => {
    if (!isTauri()) return;

    const applyShowMode = async () => {
      try {
        // Small delay to ensure Tauri windows are ready
        await new Promise((resolve) => setTimeout(resolve, 100));

        // Read directly from localStorage to get initial value before Zustand hydrates
        const stored = localStorage.getItem("claudeminder-settings");
        if (stored) {
          const settings = JSON.parse(stored);
          const mode = settings.state?.showMode;
          // Validate mode before invoke
          if (mode === "main" || mode === "overlay" || mode === "both") {
            await invoke("apply_show_mode", { mode });
          } else {
            await invoke("apply_show_mode", { mode: "main" });
          }
        }
      } catch (err) {
        console.error("Failed to apply show mode:", err);
      }
    };

    applyShowMode();
  }, []);

  useEffect(() => {
    // Skip Tauri event listeners in browser mode
    if (!isTauri()) return;

    const setupListeners = async () => {
      const unlistenSnooze = await listen(
        "snooze-activated",
        (event: { payload: { minutes: number } }) => {
          const { minutes } = event.payload;
          const snoozeUntilTime = Date.now() + minutes * 60000;
          setSnoozeUntil(snoozeUntilTime);
        },
      );

      const unlistenSettings = await listen("open-settings", () => {
        setShowSettings(true);
      });

      const unlistenRefresh = await listen("refresh-usage", () => {
        refresh();
      });

      return () => {
        unlistenSnooze();
        unlistenSettings();
        unlistenRefresh();
      };
    };

    const cleanupPromise = setupListeners();
    return () => {
      cleanupPromise.then((cleanup) => cleanup());
    };
  }, [refresh]);

  useEffect(() => {
    if (!usage?.five_hour) return;

    const checkReminders = () => {
      if (snoozeUntil && Date.now() < snoozeUntil) return;

      const resetTime = new Date(usage.five_hour!.resets_at).getTime();
      const now = Date.now();
      const remainingMins = Math.floor((resetTime - now) / 60000);

      for (const reminderMin of REMINDER_MINUTES) {
        if (
          remainingMins <= reminderMin &&
          remainingMins > reminderMin - 1 &&
          !notifiedMinutesRef.current.has(reminderMin)
        ) {
          notifyResetSoon(remainingMins);
          notifiedMinutesRef.current.add(reminderMin);
        }
      }

      if (remainingMins <= 0) {
        notifiedMinutesRef.current.clear();
        setSnoozeUntil(null);
      }
    };

    checkReminders();
    const interval = setInterval(checkReminders, 30000);
    return () => clearInterval(interval);
  }, [usage, snoozeUntil]);

  if (loading && !usage) {
    return (
      <div className={styles.app}>
        <div className={styles.background} />
        <div className={styles.loadingState}>
          <div className={styles.spinner} />
          <p className={styles.loadingText}>
            {t("dashboard.loading", "Loading...")}
          </p>
        </div>
      </div>
    );
  }

  if (isOffline) {
    return (
      <div className={styles.app}>
        <div className={styles.background} />
        <div className={styles.offlineState}>
          <GlassCard className={styles.errorCard}>
            <h3 className={styles.errorTitle}>
              {t("dashboard.offline", "Offline Mode")}
            </h3>
            <p className={styles.errorMessage}>
              {t(
                "dashboard.offlineMessage",
                "Claudeminder is offline. Retrying automatically...",
              )}
            </p>
            <button onClick={refresh} className={styles.retryButton}>
              {t("dashboard.retry", "Retry Now")}
            </button>
          </GlassCard>
        </div>
      </div>
    );
  }

  if (isRateLimited) {
    return (
      <div className={styles.app}>
        <div className={styles.background} />
        <div className={styles.errorState}>
          <GlassCard className={styles.errorCard}>
            <h3 className={styles.errorTitle}>
              {t("dashboard.rateLimited", "Rate Limited")}
            </h3>
            <p className={styles.errorMessage}>
              {t(
                "dashboard.rateLimitedMessage",
                "API rate limit exceeded. Retrying with backoff...",
              )}
            </p>
          </GlassCard>
        </div>
      </div>
    );
  }

  if (error && !usage) {
    return (
      <div className={styles.app}>
        <div className={styles.background} />
        <div className={styles.errorState}>
          <GlassCard className={styles.errorCard}>
            <h3 className={styles.errorTitle}>
              {t("dashboard.error", "Error")}
            </h3>
            <p className={styles.errorMessage}>{error}</p>
            <button onClick={refresh} className={styles.retryButton}>
              {t("dashboard.retry", "Retry")}
            </button>
          </GlassCard>
        </div>
      </div>
    );
  }

  const fiveHour = usage?.five_hour;
  const percentage = fiveHour ? fiveHour.utilization : 0;
  const resetTime = fiveHour ? new Date(fiveHour.resets_at) : new Date();

  return (
    <div className={styles.app}>
      <div className={styles.background} />

      <header className={styles.header}>
        <motion.h1
          className={styles.headerTitle}
          initial={{ opacity: 0, y: -10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.3 }}
        >
          {t("dashboard.title", "Claude Usage")}
        </motion.h1>
        <div className={styles.headerActions}>
          <button
            className={styles.iconButton}
            onClick={refresh}
            title={t("dashboard.refresh", "Refresh")}
          >
            ↻
          </button>
          <button
            className={`${styles.iconButton} ${showSettings ? styles.active : ""}`}
            onClick={() => setShowSettings(!showSettings)}
            title={t("settings.title", "Settings")}
          >
            ⚙
          </button>
        </div>
      </header>

      <main className={styles.main}>
        <motion.div
          className={styles.progressSection}
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.4, delay: 0.1 }}
        >
          <CircularProgress
            value={percentage}
            size="lg"
            showLabel
            label={t("dashboard.usage", "Used")}
            color={
              percentage > 80
                ? "error"
                : percentage > 60
                  ? "warning"
                  : "default"
            }
          />
          <ResetCountdown resetTime={resetTime} onReset={refresh} />
        </motion.div>
      </main>

      <footer className={styles.footer}>
        <FocusModeToggle
          enabled={focusMode}
          onToggle={() => setFocusMode(!focusMode)}
        />
      </footer>

      <SettingsPanel
        open={showSettings}
        onClose={() => setShowSettings(false)}
      />
    </div>
  );
}

export default App;
