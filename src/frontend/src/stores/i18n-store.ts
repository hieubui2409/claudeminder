import { create } from "zustand";
import { persist } from "zustand/middleware";
import i18n from "../i18n";

interface I18nStore {
  language: "en" | "vi";
  setLanguage: (lang: "en" | "vi") => void;
}

export const useI18nStore = create<I18nStore>()(
  persist(
    (set) => ({
      language: "en",
      setLanguage: (lang) => {
        set({ language: lang });
        i18n.changeLanguage(lang);
      },
    }),
    { name: "claudeminder-language" },
  ),
);
