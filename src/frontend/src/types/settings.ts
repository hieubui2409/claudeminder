export type ShowMode = "main" | "overlay" | "both";

export interface AppSettings {
  theme: string;
  locale: string;
  focusMode: boolean;
}

export interface ReminderSettings {
  enabled: boolean;
  strategy: "before_reset" | "on_reset" | "custom";
  customMinutes?: number;
}
