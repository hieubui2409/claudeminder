import { useTranslation } from "react-i18next";
import { useThemeStore } from "../../stores/theme-store";
import type { ThemeName } from "../../types/theme";
import styles from "./settings-controls.module.css";

const themes: { value: ThemeName; label: string }[] = [
  { value: "system", label: "System" },
  { value: "light", label: "Light" },
  { value: "dark", label: "Dark" },
];

export function ThemeSwitcher() {
  const { t } = useTranslation();
  const { theme, setTheme } = useThemeStore();

  return (
    <div className={styles.control}>
      <label className={styles.label} htmlFor="theme-select">
        {t("settings.theme", "Theme")}
      </label>
      <select
        id="theme-select"
        className={styles.select}
        value={theme}
        onChange={(e) => setTheme(e.target.value as ThemeName)}
      >
        {themes.map((opt) => (
          <option key={opt.value} value={opt.value}>
            {opt.label}
          </option>
        ))}
      </select>
    </div>
  );
}
