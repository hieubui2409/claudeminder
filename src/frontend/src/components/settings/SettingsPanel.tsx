import { useEffect, useCallback } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { useTranslation } from "react-i18next";
import { ThemeSwitcher } from "./theme-switcher";
import { LanguageSwitcher } from "./language-switcher";
import { FontSizeSlider } from "./font-size-slider";
import { RefreshIntervalSlider } from "./refresh-interval-slider";
import { ReminderSettings } from "./reminder-settings";
import { DisplayModeSelect } from "./display-mode-select";
import styles from "./SettingsPanel.module.css";

interface SettingsPanelProps {
  open: boolean;
  onClose: () => void;
}

export function SettingsPanel({ open, onClose }: SettingsPanelProps) {
  const { t } = useTranslation();

  const handleEscKey = useCallback(
    (e: KeyboardEvent) => {
      if (e.key === "Escape") onClose();
    },
    [onClose],
  );

  useEffect(() => {
    if (open) {
      document.addEventListener("keydown", handleEscKey);
      document.body.style.overflow = "hidden";
    }
    return () => {
      document.removeEventListener("keydown", handleEscKey);
      document.body.style.overflow = "";
    };
  }, [open, handleEscKey]);

  return (
    <AnimatePresence>
      {open && (
        <>
          <motion.div
            className={styles.overlay}
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.2 }}
            onClick={onClose}
          />
          <motion.aside
            className={styles.panel}
            initial={{ x: "100%" }}
            animate={{ x: 0 }}
            exit={{ x: "100%" }}
            transition={{ type: "spring", damping: 30, stiffness: 300 }}
          >
            <header className={styles.header}>
              <h2 className={styles.title}>
                {t("settings.title", "Settings")}
              </h2>
              <button
                className={styles.closeButton}
                onClick={onClose}
                aria-label={t("common.close", "Close")}
              >
                ✕
              </button>
            </header>

            <div className={styles.content}>
              <section className={styles.section}>
                <h3 className={styles.sectionTitle}>
                  {t("settings.general", "General")}
                </h3>
                <div className={styles.sectionContent}>
                  <RefreshIntervalSlider />
                  <DisplayModeSelect />
                </div>
              </section>

              <section className={styles.section}>
                <h3 className={styles.sectionTitle}>
                  {t("settings.reminders", "Reminders")}
                </h3>
                <div className={styles.sectionContent}>
                  <ReminderSettings />
                </div>
              </section>

              <section className={styles.section}>
                <h3 className={styles.sectionTitle}>
                  {t("settings.appearance", "Appearance")}
                </h3>
                <div className={styles.sectionContent}>
                  <ThemeSwitcher />
                  <FontSizeSlider />
                </div>
              </section>

              <section className={styles.section}>
                <h3 className={styles.sectionTitle}>
                  {t("settings.language", "Language")}
                </h3>
                <div className={styles.sectionContent}>
                  <LanguageSwitcher />
                </div>
              </section>
            </div>

            <div className={styles.versionInfo}>
              <span className={styles.versionText}>Claudeminder v1.0.0</span>
            </div>
          </motion.aside>
        </>
      )}
    </AnimatePresence>
  );
}
