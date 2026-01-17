import { useTranslation } from "react-i18next";
import { useSettingsStore } from "../../stores/settings-store";
import styles from "./settings-controls.module.css";

export function RefreshIntervalSlider() {
  const { t } = useTranslation();
  const { refreshInterval, setRefreshInterval } = useSettingsStore();

  const min = 30;
  const max = 300;
  const fillPercent = ((refreshInterval - min) / (max - min)) * 100;

  const sliderStyle = {
    background: `linear-gradient(to right, #6366f1 0%, #8b5cf6 ${fillPercent}%, rgba(255,255,255,0.1) ${fillPercent}%)`,
  };

  return (
    <div className={styles.sliderControl}>
      <div className={styles.sliderHeader}>
        <label className={styles.label} htmlFor="refresh-interval">
          {t("settings.refreshInterval", "Auto Refresh")}
        </label>
        <span className={styles.sliderValue}>{refreshInterval}s</span>
      </div>
      <input
        type="range"
        id="refresh-interval"
        className={styles.slider}
        style={sliderStyle}
        min={min}
        max={max}
        step="30"
        value={refreshInterval}
        onChange={(e) => setRefreshInterval(Number(e.target.value))}
      />
      <div className={styles.sliderLabels}>
        <span>30s</span>
        <span>2m</span>
        <span>5m</span>
      </div>
    </div>
  );
}
