import { useTranslation } from "react-i18next";
import styles from "./FocusModeToggle.module.css";

interface FocusModeToggleProps {
  enabled: boolean;
  onToggle: () => void;
  className?: string;
}

export function FocusModeToggle({
  enabled,
  onToggle,
  className = "",
}: FocusModeToggleProps) {
  const { t } = useTranslation();
  const classes = [styles.toggle, enabled ? styles.active : "", className]
    .filter(Boolean)
    .join(" ");

  return (
    <button
      className={classes}
      onClick={onToggle}
      aria-pressed={enabled}
      title={t("settings.focusMode.description", "Hide distractions")}
    >
      <svg
        className={styles.icon}
        viewBox="0 0 24 24"
        fill="none"
        stroke="currentColor"
        strokeWidth="2"
        strokeLinecap="round"
        strokeLinejoin="round"
      >
        <circle cx="12" cy="12" r="10" />
        <circle cx="12" cy="12" r="6" />
        <circle cx="12" cy="12" r="2" />
      </svg>
      <span className={styles.label}>
        {t("settings.focusMode.label", "Focus")}
      </span>
    </button>
  );
}
