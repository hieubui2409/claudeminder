import { create } from "zustand";
import { persist } from "zustand/middleware";
import type { ThemeName } from "../types/theme";

export type ColorLevel = "basic" | "advanced" | "expert";

export interface ColorScheme {
  bgPrimary?: string;
  bgSecondary?: string;
  textPrimary?: string;
  textSecondary?: string;
  accent?: string;
  success?: string;
  warning?: string;
  danger?: string;
}

interface ThemeStore {
  theme: ThemeName;
  colorLevel: ColorLevel;
  accentColor: string;
  customColors: ColorScheme;
  setTheme: (theme: ThemeName) => void;
  setColorLevel: (level: ColorLevel) => void;
  setAccentColor: (color: string) => void;
  setCustomColors: (colors: ColorScheme) => void;
}

export const useThemeStore = create<ThemeStore>()(
  persist(
    (set, get) => ({
      theme: "dark",
      colorLevel: "basic",
      accentColor: "#6366f1",
      customColors: {},
      setTheme: (theme) => {
        set({ theme });
        applyTheme(theme, get().customColors);
      },
      setColorLevel: (level) => set({ colorLevel: level }),
      setAccentColor: (color) => {
        set({ accentColor: color });
        if (get().colorLevel === "advanced") {
          document.documentElement.style.setProperty("--accent", color);
        }
      },
      setCustomColors: (colors) => {
        set({ customColors: colors });
        if (get().colorLevel === "expert") {
          Object.entries(colors).forEach(([key, value]) => {
            const cssVar = `--${key.replace(/([A-Z])/g, "-$1").toLowerCase()}`;
            document.documentElement.style.setProperty(cssVar, value);
          });
        }
      },
    }),
    {
      name: "claudeminder-theme",
    },
  ),
);

function applyTheme(theme: ThemeName, customColors: ColorScheme) {
  const root = document.documentElement;

  if (theme === "system") {
    const prefersDark = window.matchMedia(
      "(prefers-color-scheme: dark)",
    ).matches;
    root.setAttribute("data-theme", prefersDark ? "dark" : "light");
  } else {
    root.setAttribute("data-theme", theme);
  }

  // Apply custom colors if in advanced/expert mode
  if (Object.keys(customColors).length > 0) {
    Object.entries(customColors).forEach(([key, value]) => {
      const cssVar = `--${key.replace(/([A-Z])/g, "-$1").toLowerCase()}`;
      root.style.setProperty(cssVar, value);
    });
  }
}
