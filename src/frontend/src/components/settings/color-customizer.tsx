import { useTranslation } from "react-i18next";
import { useThemeStore } from "../../stores/theme-store";

export function ColorCustomizer() {
  const { t } = useTranslation();
  const {
    colorLevel,
    setColorLevel,
    accentColor,
    setAccentColor,
    customColors,
    setCustomColors,
  } = useThemeStore();

  return (
    <div className="color-customizer">
      <label>{t("settings.colors")}</label>

      <div className="color-level-selector">
        <button
          className={colorLevel === "basic" ? "active" : ""}
          onClick={() => setColorLevel("basic")}
        >
          {t("colorLevels.basic")}
        </button>
        <button
          className={colorLevel === "advanced" ? "active" : ""}
          onClick={() => setColorLevel("advanced")}
        >
          {t("colorLevels.advanced")}
        </button>
        <button
          className={colorLevel === "expert" ? "active" : ""}
          onClick={() => setColorLevel("expert")}
        >
          {t("colorLevels.expert")}
        </button>
      </div>

      {colorLevel === "advanced" && (
        <div className="accent-picker">
          <label htmlFor="accent-color">Accent Color</label>
          <input
            type="color"
            id="accent-color"
            value={accentColor}
            onChange={(e) => setAccentColor(e.target.value)}
          />
        </div>
      )}

      {colorLevel === "expert" && (
        <div className="full-customization">
          <div className="color-input">
            <label>Background Primary</label>
            <input
              type="color"
              value={customColors.bgPrimary || "#1a1a1a"}
              onChange={(e) =>
                setCustomColors({ ...customColors, bgPrimary: e.target.value })
              }
            />
          </div>
          <div className="color-input">
            <label>Text Primary</label>
            <input
              type="color"
              value={customColors.textPrimary || "#ffffff"}
              onChange={(e) =>
                setCustomColors({
                  ...customColors,
                  textPrimary: e.target.value,
                })
              }
            />
          </div>
          <div className="color-input">
            <label>Accent</label>
            <input
              type="color"
              value={customColors.accent || "#00e5ff"}
              onChange={(e) =>
                setCustomColors({ ...customColors, accent: e.target.value })
              }
            />
          </div>
        </div>
      )}
    </div>
  );
}
