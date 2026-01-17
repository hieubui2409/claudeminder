export type ThemeName =
  | "light"
  | "dark"
  | "neon-light"
  | "neon-dark"
  | "glass-light"
  | "glass-dark"
  | "system";

export interface ThemeColors {
  primary: string;
  secondary: string;
  background: string;
  surface: string;
  text: string;
  textSecondary: string;
  border: string;
  accent: string;
}
