import { create } from "zustand";
import { persist } from "zustand/middleware";

export type ProgressBarType = "linear" | "circular" | "gauge";

interface SettingsStore {
  fontSize: number; // 50-150
  progressBarType: ProgressBarType;
  focusMode: boolean;
  refreshInterval: number; // seconds (30-300)
  setFontSize: (size: number) => void;
  setProgressBarType: (type: ProgressBarType) => void;
  setFocusMode: (enabled: boolean) => void;
  setRefreshInterval: (seconds: number) => void;
}

export const useSettingsStore = create<SettingsStore>()(
  persist(
    (set) => ({
      fontSize: 100,
      progressBarType: "circular",
      focusMode: false,
      refreshInterval: 60, // Default 60 seconds
      setFontSize: (size) => {
        const clamped = Math.max(50, Math.min(150, size));
        set({ fontSize: clamped });
        document.documentElement.style.fontSize = `${clamped}%`;
      },
      setProgressBarType: (type) => set({ progressBarType: type }),
      setFocusMode: (enabled) => set({ focusMode: enabled }),
      setRefreshInterval: (seconds) => {
        const clamped = Math.max(30, Math.min(300, seconds));
        set({ refreshInterval: clamped });
      },
    }),
    {
      name: "claudeminder-settings",
    },
  ),
);
