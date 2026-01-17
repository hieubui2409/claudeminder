import { useTranslation } from "react-i18next";
import { useSettingsStore } from "../../stores/settings-store";
import styles from "./settings-controls.module.css";

export function FontSizeSlider() {
  const { t } = useTranslation();
  const { fontSize, setFontSize } = useSettingsStore();

  // Use symmetric range: 50% to 150% with 100% in the middle
  const min = 50;
  const max = 150;
  const fillPercent = ((fontSize - min) / (max - min)) * 100;

  const sliderStyle = {
    background: `linear-gradient(to right, #6366f1 0%, #8b5cf6 ${fillPercent}%, rgba(255,255,255,0.1) ${fillPercent}%)`,
  };

  return (
    <div className={styles.sliderControl}>
      <div className={styles.sliderHeader}>
        <label className={styles.label} htmlFor="font-size">
          {t("settings.fontSize", "Font Size")}
        </label>
        <span className={styles.sliderValue}>{fontSize}%</span>
      </div>
      <input
        type="range"
        id="font-size"
        className={styles.slider}
        style={sliderStyle}
        min={min}
        max={max}
        step="10"
        value={fontSize}
        onChange={(e) => setFontSize(Number(e.target.value))}
      />
      <div className={styles.sliderLabels}>
        <span>50%</span>
        <span>100%</span>
        <span>150%</span>
      </div>
    </div>
  );
}
