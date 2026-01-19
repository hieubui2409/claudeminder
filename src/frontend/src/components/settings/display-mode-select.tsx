import { useTranslation } from "react-i18next";
import { useSettingsStore } from "../../stores/settings-store";
import type { ShowMode } from "../../types/settings";
import styles from "./settings-controls.module.css";

export function DisplayModeSelect() {
  const { t } = useTranslation();
  const { showMode, setShowMode } = useSettingsStore();

  const options: { value: ShowMode; label: string }[] = [
    { value: "main", label: t("settings.showMode.main", "Main window only") },
    {
      value: "overlay",
      label: t("settings.showMode.overlay", "Overlay only"),
    },
    { value: "both", label: t("settings.showMode.both", "Both windows") },
  ];

  return (
    <div className={styles.control}>
      <label className={styles.label} htmlFor="show-mode">
        {t("settings.showMode.label", "Display on startup")}
      </label>
      <select
        id="show-mode"
        className={styles.select}
        value={showMode}
        onChange={(e) => setShowMode(e.target.value as ShowMode)}
      >
        {options.map((opt) => (
          <option key={opt.value} value={opt.value}>
            {opt.label}
          </option>
        ))}
      </select>
    </div>
  );
}
