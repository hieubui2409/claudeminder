import { useCallback, useEffect } from "react";
import { useThemeStore } from "../stores/theme-store";
import type { ThemeName } from "../types/theme";

interface UseThemeResult {
  theme: ThemeName;
  setTheme: (theme: ThemeName) => void;
  applyTheme: (themeName?: ThemeName) => void;
}

const getSystemTheme = (): "light" | "dark" => {
  if (typeof window === "undefined") return "light";
  return window.matchMedia("(prefers-color-scheme: dark)").matches
    ? "dark"
    : "light";
};

export function useTheme(): UseThemeResult {
  const { theme, setTheme } = useThemeStore();

  const applyTheme = useCallback(
    (themeName?: ThemeName) => {
      const themeToApply = themeName ?? theme;
      const resolvedTheme =
        themeToApply === "system" ? getSystemTheme() : themeToApply;
      document.documentElement.setAttribute("data-theme", resolvedTheme);
    },
    [theme],
  );

  useEffect(() => {
    applyTheme(theme);
  }, [theme, applyTheme]);

  useEffect(() => {
    if (theme !== "system") return;

    const mediaQuery = window.matchMedia("(prefers-color-scheme: dark)");
    const handleChange = () => applyTheme("system");

    mediaQuery.addEventListener("change", handleChange);
    return () => mediaQuery.removeEventListener("change", handleChange);
  }, [theme, applyTheme]);

  return {
    theme,
    setTheme,
    applyTheme,
  };
}
