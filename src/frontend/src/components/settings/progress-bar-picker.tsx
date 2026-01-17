import { useTranslation } from "react-i18next";
import {
  useSettingsStore,
  type ProgressBarType,
} from "../../stores/settings-store";

export function ProgressBarPicker() {
  const { t } = useTranslation();
  const { progressBarType, setProgressBarType } = useSettingsStore();

  const types: ProgressBarType[] = ["linear", "circular", "gauge"];

  return (
    <div className="progress-bar-picker">
      <label>{t("settings.progressBar")}</label>
      <div className="type-buttons">
        {types.map((type) => (
          <button
            key={type}
            className={progressBarType === type ? "active" : ""}
            onClick={() => setProgressBarType(type)}
          >
            {t(`progressTypes.${type}`)}
          </button>
        ))}
      </div>
    </div>
  );
}
