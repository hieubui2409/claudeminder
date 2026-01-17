import { useState, useEffect, useCallback } from "react";
import { invoke } from "@tauri-apps/api/core";
import { useTranslation } from "react-i18next";
import { isTauri } from "../../utils/mock-data";
import styles from "./settings-controls.module.css";

interface ReminderConfig {
  enabled: boolean;
  before_reset_minutes: number[];
  on_reset: boolean;
  custom_command: string | null;
}

interface AppConfig {
  reminder: ReminderConfig;
}

export function ReminderSettings() {
  const { t } = useTranslation();
  const [config, setConfig] = useState<ReminderConfig>({
    enabled: true,
    before_reset_minutes: [30, 15, 5],
    on_reset: true,
    custom_command: null,
  });
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [customCommand, setCustomCommand] = useState("");

  // Load config on mount
  useEffect(() => {
    const loadConfig = async () => {
      if (!isTauri()) {
        setLoading(false);
        return;
      }

      try {
        const result = await invoke<{ config: AppConfig }>("get_config");
        if (result.config?.reminder) {
          setConfig(result.config.reminder);
          setCustomCommand(result.config.reminder.custom_command || "");
        }
      } catch (error) {
        console.error("Failed to load config:", error);
      } finally {
        setLoading(false);
      }
    };

    loadConfig();
  }, []);

  // Save config
  const saveConfig = useCallback(
    async (updates: Partial<ReminderConfig>) => {
      if (!isTauri()) return;

      setSaving(true);
      try {
        const newConfig = { ...config, ...updates };
        await invoke("set_config", {
          configJson: JSON.stringify({ reminder: newConfig }),
        });
        setConfig(newConfig);
      } catch (error) {
        console.error("Failed to save config:", error);
      } finally {
        setSaving(false);
      }
    },
    [config],
  );

  // Handle custom command change with debounce
  const handleCommandChange = (value: string) => {
    setCustomCommand(value);
  };

  const handleCommandBlur = () => {
    if (customCommand !== (config.custom_command || "")) {
      saveConfig({ custom_command: customCommand || null });
    }
  };

  // Toggle reminder time
  const toggleReminderTime = (minutes: number) => {
    const current = config.before_reset_minutes;
    const newTimes = current.includes(minutes)
      ? current.filter((m) => m !== minutes)
      : [...current, minutes].sort((a, b) => b - a);
    saveConfig({ before_reset_minutes: newTimes });
  };

  if (loading) {
    return (
      <div className={styles.sliderControl}>
        <span className={styles.label}>Loading...</span>
      </div>
    );
  }

  const reminderTimes = [60, 30, 15, 5];

  return (
    <div className={styles.reminderSettings}>
      {/* Enable/Disable */}
      <div className={styles.toggleRow}>
        <label className={styles.label}>
          {t("settings.remindersEnabled", "Enable Reminders")}
        </label>
        <button
          className={`${styles.toggle} ${config.enabled ? styles.toggleActive : ""}`}
          onClick={() => saveConfig({ enabled: !config.enabled })}
          disabled={saving}
        >
          <span className={styles.toggleThumb} />
        </button>
      </div>

      {config.enabled && (
        <>
          {/* Reminder times */}
          <div className={styles.checkboxGroup}>
            <label className={styles.groupLabel}>
              {t("settings.remindBefore", "Remind before reset")}
            </label>
            <div className={styles.chipContainer}>
              {reminderTimes.map((minutes) => (
                <button
                  key={minutes}
                  className={`${styles.chip} ${config.before_reset_minutes.includes(minutes) ? styles.chipActive : ""}`}
                  onClick={() => toggleReminderTime(minutes)}
                  disabled={saving}
                >
                  {minutes >= 60 ? `${minutes / 60}h` : `${minutes}m`}
                </button>
              ))}
            </div>
          </div>

          {/* On reset */}
          <div className={styles.toggleRow}>
            <label className={styles.label}>
              {t("settings.remindOnReset", "Notify on reset")}
            </label>
            <button
              className={`${styles.toggle} ${config.on_reset ? styles.toggleActive : ""}`}
              onClick={() => saveConfig({ on_reset: !config.on_reset })}
              disabled={saving}
            >
              <span className={styles.toggleThumb} />
            </button>
          </div>

          {/* Custom command */}
          <div className={styles.inputGroup}>
            <label className={styles.label} htmlFor="custom-command">
              {t("settings.customCommand", "Run command on reminder")}
            </label>
            <input
              id="custom-command"
              type="text"
              className={styles.textInput}
              placeholder='e.g., claude -p "Start new session"'
              value={customCommand}
              onChange={(e) => handleCommandChange(e.target.value)}
              onBlur={handleCommandBlur}
              disabled={saving}
            />
            <span className={styles.hint}>
              {t(
                "settings.customCommandHint",
                "Shell command to execute when reminder triggers",
              )}
            </span>
          </div>
        </>
      )}
    </div>
  );
}
