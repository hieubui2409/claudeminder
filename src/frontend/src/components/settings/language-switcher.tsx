import { useTranslation } from "react-i18next";
import { useI18nStore } from "../../stores/i18n-store";
import styles from "./settings-controls.module.css";

const languages: { value: "en" | "vi"; label: string }[] = [
  { value: "en", label: "English" },
  { value: "vi", label: "Tiếng Việt" },
];

export function LanguageSwitcher() {
  const { t } = useTranslation();
  const { language, setLanguage } = useI18nStore();

  return (
    <div className={styles.control}>
      <label className={styles.label} htmlFor="language-select">
        {t("settings.language", "Language")}
      </label>
      <select
        id="language-select"
        className={styles.select}
        value={language}
        onChange={(e) => setLanguage(e.target.value as "en" | "vi")}
      >
        {languages.map((lang) => (
          <option key={lang.value} value={lang.value}>
            {lang.label}
          </option>
        ))}
      </select>
    </div>
  );
}
