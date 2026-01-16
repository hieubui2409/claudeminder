---
title: "Phase 3: Frontend UI"
status: pending
priority: P1
effort: 8h
---

# Phase 3: React Components with Themes & Customization

## Context Links

- [UI Themes Research](../reports/researcher-260117-024115-ui-themes-design.md)
- [Tauri Rules](../../02-general/rules/02-tauri.md)

## Overview

Build React UI components for dashboard with 6 theme variants (default: Neon Dark), customizable layout, 3 progress bar styles, layered color customization, font size control, and i18n (en + vi). Use Zustand for state, CSS custom properties for theming, react-grid-layout for drag-drop, react-i18next for translations.

## Key Insights (from research + interview)

- Glassmorphism: `backdrop-filter: blur(12px)` + rgba backgrounds
- Neon: Layered `text-shadow` + `box-shadow` glows
- Default theme: Neon Dark (user customizable)
- Color customization: 3 levels (preset → accent picker → full scheme)
- Dashboard layout: User can drag-drop widgets
- Progress bar: 3 variants (linear/circular/gauge) - user choice
- Countdown: Show both HH:MM:SS + human readable (e.g., "2h 34m left")
- Font size: 80%-150% slider
- i18n: en + vi with react-i18next
- Goals: Budget bar + pace indicator
- Focus mode: Status indicator in UI

## Requirements

### Functional

- Dashboard displays: usage %, reset countdown, stats, goals
- Theme switcher with 6 options + system auto (default: neon-dark)
- Progress bar with 3 variants: linear/circular/gauge (user setting)
- Layered color customization:
  - Basic: Theme presets (6 themes)
  - Advanced: Accent color picker
  - Expert: Full color scheme editor
- Drag-drop dashboard layout (save positions)
- Font size slider (80%-150%)
- i18n: English + Vietnamese
- Countdown: Dual format (HH:MM:SS + human readable)
- Goals widget: Budget bar + pace indicator
- Focus mode UI indicator
- Smooth theme transitions (0.3s ease)

### Non-Functional

- WCAG AA contrast compliance
- < 16ms render time
- Works without JS (basic HTML fallback)
- Responsive layout (desktop + system tray)

## Architecture

```
src/frontend/src/
├── components/
│   ├── dashboard/
│   │   ├── dashboard-widget.tsx       # Main container
│   │   ├── usage-display.tsx          # Progress bar (3 variants)
│   │   ├── reset-countdown.tsx        # Timer (dual format)
│   │   ├── stats-panel.tsx            # Requests/tokens
│   │   ├── goals-widget.tsx           # Budget + pace
│   │   ├── focus-mode-indicator.tsx   # Focus status
│   │   └── grid-layout-wrapper.tsx    # Drag-drop container
│   ├── settings/
│   │   ├── theme-switcher.tsx         # Theme selector
│   │   ├── color-customizer.tsx       # 3-tier color panel
│   │   ├── progress-bar-picker.tsx    # Linear/circular/gauge
│   │   ├── font-size-slider.tsx       # 80%-150%
│   │   └── language-switcher.tsx      # en/vi
│   └── ui/
│       ├── glass-card.tsx             # Reusable glass container
│       ├── neon-text.tsx              # Neon glow text
│       ├── circular-progress.tsx      # Circular variant
│       └── gauge-progress.tsx         # Gauge variant
├── styles/
│   ├── globals.css                    # CSS reset + vars
│   ├── themes/
│   │   ├── light.css
│   │   ├── dark.css
│   │   ├── neon-light.css
│   │   ├── neon-dark.css              # DEFAULT
│   │   ├── glass-light.css
│   │   └── glass-dark.css
│   └── components/
│       ├── dashboard.css
│       ├── progress-bar.css
│       └── settings.css
├── stores/
│   ├── usage-store.ts                 # Usage data state
│   ├── theme-store.ts                 # Theme + colors
│   ├── settings-store.ts              # Layout, fontSize, progressType
│   └── i18n-store.ts                  # Language preference
├── hooks/
│   ├── use-usage.ts                   # (from Phase 2)
│   ├── use-countdown.ts               # Timer logic
│   ├── use-theme.ts                   # Theme management
│   └── use-grid-layout.ts             # Layout state
├── i18n/
│   ├── index.ts                       # i18next setup
│   ├── en.json                        # English translations
│   └── vi.json                        # Vietnamese translations
└── App.tsx                            # Root component
```

## Related Code Files

### Create

- `src/frontend/src/components/dashboard/dashboard-widget.tsx`
- `src/frontend/src/components/dashboard/usage-display.tsx`
- `src/frontend/src/components/dashboard/reset-countdown.tsx`
- `src/frontend/src/components/dashboard/stats-panel.tsx`
- `src/frontend/src/components/dashboard/goals-widget.tsx`
- `src/frontend/src/components/dashboard/focus-mode-indicator.tsx`
- `src/frontend/src/components/dashboard/grid-layout-wrapper.tsx`
- `src/frontend/src/components/settings/theme-switcher.tsx`
- `src/frontend/src/components/settings/color-customizer.tsx`
- `src/frontend/src/components/settings/progress-bar-picker.tsx`
- `src/frontend/src/components/settings/font-size-slider.tsx`
- `src/frontend/src/components/settings/language-switcher.tsx`
- `src/frontend/src/components/ui/glass-card.tsx`
- `src/frontend/src/components/ui/neon-text.tsx`
- `src/frontend/src/components/ui/circular-progress.tsx`
- `src/frontend/src/components/ui/gauge-progress.tsx`
- `src/frontend/src/styles/globals.css`
- `src/frontend/src/styles/themes/light.css`
- `src/frontend/src/styles/themes/dark.css`
- `src/frontend/src/styles/themes/neon-light.css`
- `src/frontend/src/styles/themes/neon-dark.css`
- `src/frontend/src/styles/themes/glass-light.css`
- `src/frontend/src/styles/themes/glass-dark.css`
- `src/frontend/src/styles/components/settings.css`
- `src/frontend/src/stores/usage-store.ts`
- `src/frontend/src/stores/theme-store.ts`
- `src/frontend/src/stores/settings-store.ts`
- `src/frontend/src/stores/i18n-store.ts`
- `src/frontend/src/hooks/use-countdown.ts`
- `src/frontend/src/hooks/use-theme.ts`
- `src/frontend/src/hooks/use-grid-layout.ts`
- `src/frontend/src/i18n/index.ts`
- `src/frontend/src/i18n/en.json`
- `src/frontend/src/i18n/vi.json`

### Modify

- `src/frontend/src/App.tsx`
- `src/frontend/src/main.tsx`
- `src/frontend/package.json` (add react-grid-layout, react-i18next)

## Implementation Steps

### Step 1: Install Dependencies

```bash
cd src/frontend
bun add react-grid-layout react-i18next i18next @types/react-grid-layout
```

### Step 2: Create i18n Setup

**i18n/index.ts:**

```typescript
import i18n from "i18next";
import { initReactI18next } from "react-i18next";
import en from "./en.json";
import vi from "./vi.json";

i18n.use(initReactI18next).init({
  resources: {
    en: { translation: en },
    vi: { translation: vi },
  },
  lng: "en",
  fallbackLng: "en",
  interpolation: {
    escapeValue: false,
  },
});

export default i18n;
```

**i18n/en.json:**

```json
{
  "dashboard": {
    "title": "Claude Usage",
    "usage": "Usage",
    "resetsIn": "Resets in",
    "resetComplete": "Reset Complete!",
    "refresh": "Refresh",
    "goals": "Goals",
    "budget": "Budget",
    "pace": "Pace",
    "focusMode": "Focus Mode"
  },
  "settings": {
    "theme": "Theme",
    "language": "Language",
    "fontSize": "Font Size",
    "progressBar": "Progress Bar Style",
    "colors": "Colors",
    "layout": "Layout"
  },
  "themes": {
    "system": "System",
    "light": "Light",
    "dark": "Dark",
    "neonLight": "Neon Light",
    "neonDark": "Neon Dark",
    "glassLight": "Glass Light",
    "glassDark": "Glass Dark"
  },
  "progressTypes": {
    "linear": "Linear",
    "circular": "Circular",
    "gauge": "Gauge"
  },
  "colorLevels": {
    "basic": "Theme Presets",
    "advanced": "Accent Color",
    "expert": "Full Customization"
  }
}
```

**i18n/vi.json:**

```json
{
  "dashboard": {
    "title": "Sử Dụng Claude",
    "usage": "Đã dùng",
    "resetsIn": "Reset sau",
    "resetComplete": "Đã Reset!",
    "refresh": "Làm mới",
    "goals": "Mục tiêu",
    "budget": "Ngân sách",
    "pace": "Tốc độ",
    "focusMode": "Chế độ tập trung"
  },
  "settings": {
    "theme": "Giao diện",
    "language": "Ngôn ngữ",
    "fontSize": "Cỡ chữ",
    "progressBar": "Kiểu thanh tiến trình",
    "colors": "Màu sắc",
    "layout": "Bố cục"
  },
  "themes": {
    "system": "Hệ thống",
    "light": "Sáng",
    "dark": "Tối",
    "neonLight": "Neon Sáng",
    "neonDark": "Neon Tối",
    "glassLight": "Thủy tinh Sáng",
    "glassDark": "Thủy tinh Tối"
  },
  "progressTypes": {
    "linear": "Dạng thanh",
    "circular": "Dạng tròn",
    "gauge": "Dạng đồng hồ"
  },
  "colorLevels": {
    "basic": "Giao diện có sẵn",
    "advanced": "Màu nhấn",
    "expert": "Tùy chỉnh đầy đủ"
  }
}
```

### Step 3: Create Settings Store

**stores/settings-store.ts:**

```typescript
import { create } from "zustand";
import { persist } from "zustand/middleware";

export type ProgressBarType = "linear" | "circular" | "gauge";

interface Layout {
  i: string;
  x: number;
  y: number;
  w: number;
  h: number;
}

interface SettingsStore {
  fontSize: number; // 80-150
  progressBarType: ProgressBarType;
  layout: Layout[];
  setFontSize: (size: number) => void;
  setProgressBarType: (type: ProgressBarType) => void;
  setLayout: (layout: Layout[]) => void;
}

export const useSettingsStore = create<SettingsStore>()(
  persist(
    (set) => ({
      fontSize: 100,
      progressBarType: "linear",
      layout: [
        { i: "usage", x: 0, y: 0, w: 6, h: 4 },
        { i: "countdown", x: 6, y: 0, w: 6, h: 2 },
        { i: "goals", x: 6, y: 2, w: 6, h: 2 },
        { i: "stats", x: 0, y: 4, w: 12, h: 2 },
      ],
      setFontSize: (size) => {
        set({ fontSize: Math.max(80, Math.min(150, size)) });
        document.documentElement.style.fontSize = `${size}%`;
      },
      setProgressBarType: (type) => set({ progressBarType: type }),
      setLayout: (layout) => set({ layout }),
    }),
    { name: "claudiminder-settings" },
  ),
);
```

### Step 4: Create Theme Store with Color Customization

**stores/theme-store.ts:**

```typescript
import { create } from "zustand";
import { persist } from "zustand/middleware";

export type Theme =
  | "light"
  | "dark"
  | "neon-light"
  | "neon-dark"
  | "glass-light"
  | "glass-dark"
  | "system";

export type ColorLevel = "basic" | "advanced" | "expert";

interface ColorScheme {
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
  theme: Theme;
  colorLevel: ColorLevel;
  accentColor: string;
  customColors: ColorScheme;
  setTheme: (theme: Theme) => void;
  setColorLevel: (level: ColorLevel) => void;
  setAccentColor: (color: string) => void;
  setCustomColors: (colors: ColorScheme) => void;
}

export const useThemeStore = create<ThemeStore>()(
  persist(
    (set, get) => ({
      theme: "neon-dark", // DEFAULT
      colorLevel: "basic",
      accentColor: "#00e5ff",
      customColors: {},
      setTheme: (theme) => {
        set({ theme });
        applyTheme(theme, get().customColors, get().accentColor);
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
    { name: "claudiminder-theme" },
  ),
);

function applyTheme(theme: Theme, customColors: ColorScheme, accent: string) {
  const root = document.documentElement;

  if (theme === "system") {
    const prefersDark = window.matchMedia(
      "(prefers-color-scheme: dark)",
    ).matches;
    root.className = prefersDark ? "dark" : "light";
  } else {
    root.className = theme;
  }

  // Apply custom colors if in advanced/expert mode
  if (Object.keys(customColors).length > 0) {
    Object.entries(customColors).forEach(([key, value]) => {
      const cssVar = `--${key.replace(/([A-Z])/g, "-$1").toLowerCase()}`;
      root.style.setProperty(cssVar, value);
    });
  }
}
```

### Step 5: Create i18n Store

**stores/i18n-store.ts:**

```typescript
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
    { name: "claudiminder-language" },
  ),
);
```

### Step 6: Create Global CSS with Custom Properties

**styles/globals.css:**

```css
:root {
  color-scheme: light dark;

  /* Base colors (overridden by themes/customization) */
  --bg-primary: #ffffff;
  --bg-secondary: #f5f5f5;
  --text-primary: #1a1a1a;
  --text-secondary: #666666;
  --accent: #00e5ff;
  --success: #39ff14;
  --warning: #ffff00;
  --danger: #ff0000;

  /* Glass effect */
  --glass-bg: rgba(255, 255, 255, 0.1);
  --glass-border: rgba(255, 255, 255, 0.2);
  --glass-blur: 12px;

  /* Neon glow */
  --neon-glow: 0 0 8px var(--accent), 0 0 12px var(--accent);

  /* Transitions */
  --transition-theme: background-color 0.3s ease, color 0.3s ease;
}

@media (prefers-reduced-motion: reduce) {
  :root {
    --transition-theme: none;
  }
}

* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family:
    system-ui,
    -apple-system,
    sans-serif;
  background-color: var(--bg-primary);
  color: var(--text-primary);
  transition: var(--transition-theme);
  min-height: 100vh;
  font-size: 100%; /* Dynamic via settings */
}
```

### Step 7: Create Theme CSS Files

**themes/neon-dark.css (DEFAULT):**

```css
.neon-dark {
  --bg-primary: #05081a;
  --bg-secondary: #0a0f2e;
  --text-primary: #00e5ff;
  --text-secondary: #ff00ff;
  --accent: #00e5ff;
  --neon-glow: 0 0 8px #00e5ff, 0 0 12px #00e5ff, 0 0 20px #ff00ff;
}

.neon-dark .neon-text {
  text-shadow: var(--neon-glow);
}

.neon-dark .neon-box {
  border: 2px solid var(--accent);
  box-shadow:
    0 0 10px var(--accent),
    inset 0 0 10px rgba(0, 229, 255, 0.1);
}
```

**themes/dark.css:**

```css
.dark {
  --bg-primary: #1a1a1a;
  --bg-secondary: #2a2a2a;
  --text-primary: #ffffff;
  --text-secondary: #a0a0a0;
  --glass-bg: rgba(0, 0, 0, 0.3);
}
```

**themes/light.css:**

```css
.light {
  --bg-primary: #ffffff;
  --bg-secondary: #f5f5f5;
  --text-primary: #1a1a1a;
  --text-secondary: #666666;
  --accent: #007acc;
}
```

**themes/neon-light.css:**

```css
.neon-light {
  --bg-primary: #f0f0ff;
  --bg-secondary: #e0e0ff;
  --text-primary: #ff00ff;
  --text-secondary: #00e5ff;
  --accent: #ff00ff;
  --neon-glow: 0 0 6px #ff00ff, 0 0 10px #ff00ff, 0 0 16px #00e5ff;
}

.neon-light .neon-text {
  text-shadow: var(--neon-glow);
}

.neon-light .neon-box {
  border: 2px solid var(--accent);
  box-shadow:
    0 0 8px var(--accent),
    inset 0 0 8px rgba(255, 0, 255, 0.1);
}
```

**themes/glass-dark.css:**

```css
.glass-dark {
  --bg-primary: #1a1a2e;
  --bg-secondary: transparent;
  --text-primary: #ffffff;
  --glass-bg: rgba(255, 255, 255, 0.08);
  --glass-border: rgba(255, 255, 255, 0.15);
  --glass-blur: 12px;
}
```

**themes/glass-light.css:**

```css
.glass-light {
  --bg-primary: #e8e8ff;
  --bg-secondary: transparent;
  --text-primary: #1a1a1a;
  --glass-bg: rgba(255, 255, 255, 0.5);
  --glass-border: rgba(0, 0, 0, 0.1);
  --glass-blur: 12px;
}
```

### Step 8: Create UI Components

**components/ui/glass-card.tsx:**

```tsx
import { ReactNode } from "react";

interface GlassCardProps {
  children: ReactNode;
  className?: string;
}

export function GlassCard({ children, className = "" }: GlassCardProps) {
  return (
    <div
      className={`glass-card ${className}`}
      style={{
        background: "var(--glass-bg)",
        backdropFilter: `blur(var(--glass-blur))`,
        WebkitBackdropFilter: `blur(var(--glass-blur))`,
        borderRadius: "16px",
        border: "1px solid var(--glass-border)",
        boxShadow: "0 8px 32px rgba(31, 38, 135, 0.37)",
        padding: "16px",
      }}
    >
      {children}
    </div>
  );
}
```

**components/ui/circular-progress.tsx:**

```tsx
interface CircularProgressProps {
  percentage: number;
  size?: number;
  strokeWidth?: number;
}

export function CircularProgress({
  percentage,
  size = 120,
  strokeWidth = 8,
}: CircularProgressProps) {
  const radius = (size - strokeWidth) / 2;
  const circumference = 2 * Math.PI * radius;
  const offset = circumference - (percentage / 100) * circumference;

  return (
    <svg width={size} height={size} className="circular-progress">
      <circle
        cx={size / 2}
        cy={size / 2}
        r={radius}
        fill="none"
        stroke="var(--bg-secondary)"
        strokeWidth={strokeWidth}
      />
      <circle
        cx={size / 2}
        cy={size / 2}
        r={radius}
        fill="none"
        stroke="var(--accent)"
        strokeWidth={strokeWidth}
        strokeDasharray={circumference}
        strokeDashoffset={offset}
        strokeLinecap="round"
        transform={`rotate(-90 ${size / 2} ${size / 2})`}
        style={{ transition: "stroke-dashoffset 0.3s ease" }}
      />
      <text
        x="50%"
        y="50%"
        textAnchor="middle"
        dy="0.3em"
        className="neon-text"
        style={{ fontSize: "24px", fontWeight: "bold" }}
      >
        {percentage.toFixed(1)}%
      </text>
    </svg>
  );
}
```

**components/ui/gauge-progress.tsx:**

```tsx
interface GaugeProgressProps {
  percentage: number;
  size?: number;
}

export function GaugeProgress({ percentage, size = 160 }: GaugeProgressProps) {
  const angle = (percentage / 100) * 180 - 90; // -90 to 90 degrees
  const needleLength = size / 2 - 20;

  return (
    <svg width={size} height={size / 2 + 20} className="gauge-progress">
      <defs>
        <linearGradient id="gaugeGradient" x1="0%" y1="0%" x2="100%" y2="0%">
          <stop offset="0%" stopColor="var(--success)" />
          <stop offset="50%" stopColor="var(--warning)" />
          <stop offset="100%" stopColor="var(--danger)" />
        </linearGradient>
      </defs>

      {/* Arc background */}
      <path
        d={`M 20,${size / 2} A ${size / 2 - 20},${size / 2 - 20} 0 0,1 ${size - 20},${size / 2}`}
        fill="none"
        stroke="var(--bg-secondary)"
        strokeWidth="12"
        strokeLinecap="round"
      />

      {/* Arc progress */}
      <path
        d={`M 20,${size / 2} A ${size / 2 - 20},${size / 2 - 20} 0 0,1 ${size - 20},${size / 2}`}
        fill="none"
        stroke="url(#gaugeGradient)"
        strokeWidth="12"
        strokeLinecap="round"
        strokeDasharray={`${(percentage / 100) * Math.PI * (size / 2 - 20)} ${Math.PI * (size / 2 - 20)}`}
      />

      {/* Needle */}
      <line
        x1={size / 2}
        y1={size / 2}
        x2={size / 2 + needleLength * Math.cos((angle * Math.PI) / 180)}
        y2={size / 2 + needleLength * Math.sin((angle * Math.PI) / 180)}
        stroke="var(--accent)"
        strokeWidth="3"
        strokeLinecap="round"
      />

      {/* Center dot */}
      <circle cx={size / 2} cy={size / 2} r="6" fill="var(--accent)" />

      {/* Value text */}
      <text
        x="50%"
        y={size / 2 + 30}
        textAnchor="middle"
        className="neon-text"
        style={{ fontSize: "20px", fontWeight: "bold" }}
      >
        {percentage.toFixed(1)}%
      </text>
    </svg>
  );
}
```

### Step 9: Create Usage Display with 3 Variants

**components/dashboard/usage-display.tsx:**

```tsx
import { useTranslation } from "react-i18next";
import { useSettingsStore } from "../../stores/settings-store";
import { CircularProgress } from "../ui/circular-progress";
import { GaugeProgress } from "../ui/gauge-progress";

interface UsageDisplayProps {
  percentage: number;
}

export function UsageDisplay({ percentage }: UsageDisplayProps) {
  const { t } = useTranslation();
  const { progressBarType } = useSettingsStore();

  const getColor = (pct: number) => {
    if (pct < 33) return "var(--success)";
    if (pct < 66) return "var(--warning)";
    if (pct < 90) return "#ff8800";
    return "var(--danger)";
  };

  return (
    <div className="usage-display">
      <div className="usage-header">
        <span className="label">{t("dashboard.usage")}</span>
        {progressBarType === "linear" && (
          <span className="value neon-text">{percentage.toFixed(1)}%</span>
        )}
      </div>

      {progressBarType === "linear" && (
        <div className="progress-container">
          <div
            className="progress-fill"
            style={{
              width: `${percentage}%`,
              background: `linear-gradient(90deg, var(--accent), ${getColor(percentage)})`,
            }}
          />
        </div>
      )}

      {progressBarType === "circular" && (
        <div className="progress-circular-wrapper">
          <CircularProgress percentage={percentage} />
        </div>
      )}

      {progressBarType === "gauge" && (
        <div className="progress-gauge-wrapper">
          <GaugeProgress percentage={percentage} />
        </div>
      )}
    </div>
  );
}
```

### Step 10: Create Reset Countdown with Dual Format

**components/dashboard/reset-countdown.tsx:**

```tsx
import { useTranslation } from "react-i18next";
import { useCountdown } from "../../hooks/use-countdown";

interface ResetCountdownProps {
  resetsAt: string;
}

export function ResetCountdown({ resetsAt }: ResetCountdownProps) {
  const { t } = useTranslation();
  const { hours, minutes, seconds, isExpired, humanReadable } =
    useCountdown(resetsAt);

  if (isExpired) {
    return (
      <div className="reset-countdown complete">
        <span className="neon-text">{t("dashboard.resetComplete")}</span>
      </div>
    );
  }

  return (
    <div className="reset-countdown">
      <span className="label">{t("dashboard.resetsIn")}</span>
      <span className="timer neon-text">
        {String(hours).padStart(2, "0")}:{String(minutes).padStart(2, "0")}:
        {String(seconds).padStart(2, "0")}
      </span>
      <span className="human-readable">{humanReadable}</span>
    </div>
  );
}
```

### Step 11: Create Countdown Hook with Human Readable

**hooks/use-countdown.ts:**

```typescript
import { useEffect, useState } from "react";

interface CountdownResult {
  hours: number;
  minutes: number;
  seconds: number;
  totalSeconds: number;
  isExpired: boolean;
  humanReadable: string;
}

export function useCountdown(targetDate: string): CountdownResult {
  const [totalSeconds, setTotalSeconds] = useState(0);

  useEffect(() => {
    const calculate = () => {
      const target = new Date(targetDate).getTime();
      const now = Date.now();
      const diff = Math.max(0, Math.floor((target - now) / 1000));
      setTotalSeconds(diff);
    };

    calculate();
    const interval = setInterval(calculate, 1000);
    return () => clearInterval(interval);
  }, [targetDate]);

  const hours = Math.floor(totalSeconds / 3600);
  const minutes = Math.floor((totalSeconds % 3600) / 60);
  const seconds = totalSeconds % 60;

  const humanReadable = (() => {
    if (hours > 0) {
      return `${hours}h ${minutes}m left`;
    }
    if (minutes > 0) {
      return `${minutes}m ${seconds}s left`;
    }
    return `${seconds}s left`;
  })();

  return {
    hours,
    minutes,
    seconds,
    totalSeconds,
    isExpired: totalSeconds === 0,
    humanReadable,
  };
}
```

### Step 12: Create Goals Widget

**components/dashboard/goals-widget.tsx:**

```tsx
import { useTranslation } from "react-i18next";

interface GoalsWidgetProps {
  budget: number; // e.g., 1000 requests
  current: number; // e.g., 450 requests
  pace: "on-track" | "ahead" | "behind";
}

export function GoalsWidget({ budget, current, pace }: GoalsWidgetProps) {
  const { t } = useTranslation();
  const percentage = (current / budget) * 100;

  const paceIcons = {
    "on-track": "✓",
    ahead: "↑",
    behind: "↓",
  };

  const paceColors = {
    "on-track": "var(--success)",
    ahead: "var(--accent)",
    behind: "var(--warning)",
  };

  return (
    <div className="goals-widget">
      <div className="goals-header">
        <span className="label">{t("dashboard.goals")}</span>
        <span className="pace" style={{ color: paceColors[pace] }}>
          {paceIcons[pace]} {pace}
        </span>
      </div>

      <div className="budget-bar-container">
        <div className="budget-bar">
          <div
            className="budget-fill"
            style={{
              width: `${Math.min(percentage, 100)}%`,
              background: percentage > 100 ? "var(--danger)" : "var(--accent)",
            }}
          />
        </div>
        <div className="budget-text">
          <span className="current">{current}</span>
          <span className="separator">/</span>
          <span className="total">{budget}</span>
        </div>
      </div>
    </div>
  );
}
```

### Step 13: Create Focus Mode Indicator

**components/dashboard/focus-mode-indicator.tsx:**

```tsx
import { useTranslation } from "react-i18next";

interface FocusModeIndicatorProps {
  enabled: boolean;
  onToggle: () => void;
}

export function FocusModeIndicator({
  enabled,
  onToggle,
}: FocusModeIndicatorProps) {
  const { t } = useTranslation();

  return (
    <div className={`focus-mode-indicator ${enabled ? "active" : ""}`}>
      <button onClick={onToggle} className="focus-toggle">
        <span className="icon">{enabled ? "🎯" : "💤"}</span>
        <span className="label">{t("dashboard.focusMode")}</span>
        <span className="status">{enabled ? "ON" : "OFF"}</span>
      </button>
    </div>
  );
}
```

### Step 14: Create Grid Layout Wrapper

**hooks/use-grid-layout.ts:**

```typescript
import { useSettingsStore } from "../stores/settings-store";

export function useGridLayout() {
  const { layout, setLayout } = useSettingsStore();

  const handleLayoutChange = (newLayout: any[]) => {
    setLayout(newLayout);
  };

  return { layout, handleLayoutChange };
}
```

**components/dashboard/grid-layout-wrapper.tsx:**

```tsx
import { ReactNode } from "react";
import { Responsive, WidthProvider, Layout } from "react-grid-layout";
import { useGridLayout } from "../../hooks/use-grid-layout";
import "react-grid-layout/css/styles.css";
import "react-resizable/css/styles.css";

const ResponsiveGridLayout = WidthProvider(Responsive);

interface GridLayoutWrapperProps {
  children: ReactNode;
}

export function GridLayoutWrapper({ children }: GridLayoutWrapperProps) {
  const { layout, handleLayoutChange } = useGridLayout();

  return (
    <ResponsiveGridLayout
      className="dashboard-grid"
      layouts={{ lg: layout }}
      breakpoints={{ lg: 1200, md: 996, sm: 768, xs: 480, xxs: 0 }}
      cols={{ lg: 12, md: 10, sm: 6, xs: 4, xxs: 2 }}
      rowHeight={40}
      onLayoutChange={handleLayoutChange}
      draggableHandle=".drag-handle"
    >
      {children}
    </ResponsiveGridLayout>
  );
}
```

### Step 15: Create Settings Components

**components/settings/theme-switcher.tsx:**

```tsx
import { useTranslation } from "react-i18next";
import { useThemeStore, Theme } from "../../stores/theme-store";

const themes: { value: Theme; label: string }[] = [
  { value: "system", label: "themes.system" },
  { value: "light", label: "themes.light" },
  { value: "dark", label: "themes.dark" },
  { value: "neon-light", label: "themes.neonLight" },
  { value: "neon-dark", label: "themes.neonDark" },
  { value: "glass-light", label: "themes.glassLight" },
  { value: "glass-dark", label: "themes.glassDark" },
];

export function ThemeSwitcher() {
  const { t } = useTranslation();
  const { theme, setTheme } = useThemeStore();

  return (
    <div className="theme-switcher">
      <label htmlFor="theme-select">{t("settings.theme")}</label>
      <select
        id="theme-select"
        value={theme}
        onChange={(e) => setTheme(e.target.value as Theme)}
      >
        {themes.map((t) => (
          <option key={t.value} value={t.value}>
            {t(t.label)}
          </option>
        ))}
      </select>
    </div>
  );
}
```

**components/settings/color-customizer.tsx:**

```tsx
import { useTranslation } from "react-i18next";
import { useThemeStore, ColorLevel } from "../../stores/theme-store";

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
```

**components/settings/progress-bar-picker.tsx:**

```tsx
import { useTranslation } from "react-i18next";
import { useSettingsStore, ProgressBarType } from "../../stores/settings-store";

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
```

**components/settings/font-size-slider.tsx:**

```tsx
import { useTranslation } from "react-i18next";
import { useSettingsStore } from "../../stores/settings-store";

export function FontSizeSlider() {
  const { t } = useTranslation();
  const { fontSize, setFontSize } = useSettingsStore();

  return (
    <div className="font-size-slider">
      <label htmlFor="font-size">
        {t("settings.fontSize")}: {fontSize}%
      </label>
      <input
        type="range"
        id="font-size"
        min="80"
        max="150"
        step="5"
        value={fontSize}
        onChange={(e) => setFontSize(Number(e.target.value))}
      />
      <div className="range-labels">
        <span>80%</span>
        <span>100%</span>
        <span>150%</span>
      </div>
    </div>
  );
}
```

**components/settings/language-switcher.tsx:**

```tsx
import { useTranslation } from "react-i18next";
import { useI18nStore } from "../../stores/i18n-store";

export function LanguageSwitcher() {
  const { t } = useTranslation();
  const { language, setLanguage } = useI18nStore();

  return (
    <div className="language-switcher">
      <label htmlFor="language-select">{t("settings.language")}</label>
      <select
        id="language-select"
        value={language}
        onChange={(e) => setLanguage(e.target.value as "en" | "vi")}
      >
        <option value="en">English</option>
        <option value="vi">Tiếng Việt</option>
      </select>
    </div>
  );
}
```

### Step 16: Create Dashboard Widget with Grid

**components/dashboard/dashboard-widget.tsx:**

```tsx
import { GlassCard } from "../ui/glass-card";
import { GridLayoutWrapper } from "./grid-layout-wrapper";
import { ResetCountdown } from "./reset-countdown";
import { UsageDisplay } from "./usage-display";
import { GoalsWidget } from "./goals-widget";
import { FocusModeIndicator } from "./focus-mode-indicator";
import { useUsage } from "../../hooks/use-usage";
import { useTranslation } from "react-i18next";
import { useState } from "react";

export function DashboardWidget() {
  const { t } = useTranslation();
  const { usage, loading, error, refresh } = useUsage();
  const [focusMode, setFocusMode] = useState(false);

  if (loading && !usage) {
    return (
      <GlassCard className="dashboard-widget">
        <div className="loading">Loading...</div>
      </GlassCard>
    );
  }

  if (error && !usage) {
    return (
      <GlassCard className="dashboard-widget error">
        <div className="error-message">{error}</div>
        <button onClick={refresh}>Retry</button>
      </GlassCard>
    );
  }

  const fiveHour = usage?.five_hour;

  return (
    <div className="dashboard-container">
      <header className="dashboard-header">
        <h1>{t("dashboard.title")}</h1>
        <FocusModeIndicator
          enabled={focusMode}
          onToggle={() => setFocusMode(!focusMode)}
        />
        <button onClick={refresh} className="refresh-btn">
          {t("dashboard.refresh")}
        </button>
      </header>

      <GridLayoutWrapper>
        <div key="usage" className="grid-item">
          <GlassCard className="drag-handle">
            {fiveHour && (
              <UsageDisplay percentage={fiveHour.utilization * 100} />
            )}
          </GlassCard>
        </div>

        <div key="countdown" className="grid-item">
          <GlassCard className="drag-handle">
            {fiveHour && <ResetCountdown resetsAt={fiveHour.resets_at} />}
          </GlassCard>
        </div>

        <div key="goals" className="grid-item">
          <GlassCard className="drag-handle">
            <GoalsWidget budget={1000} current={450} pace="on-track" />
          </GlassCard>
        </div>

        <div key="stats" className="grid-item">
          <GlassCard className="drag-handle">
            <div>Stats Panel (Phase 4)</div>
          </GlassCard>
        </div>
      </GridLayoutWrapper>
    </div>
  );
}
```

### Step 17: Update App.tsx

```tsx
import { useEffect } from "react";
import { DashboardWidget } from "./components/dashboard/dashboard-widget";
import { ThemeSwitcher } from "./components/settings/theme-switcher";
import { ColorCustomizer } from "./components/settings/color-customizer";
import { ProgressBarPicker } from "./components/settings/progress-bar-picker";
import { FontSizeSlider } from "./components/settings/font-size-slider";
import { LanguageSwitcher } from "./components/settings/language-switcher";
import { useThemeStore } from "./stores/theme-store";
import { useI18nStore } from "./stores/i18n-store";
import { useSettingsStore } from "./stores/settings-store";
import "./i18n";
import "./styles/globals.css";
import "./styles/themes/light.css";
import "./styles/themes/dark.css";
import "./styles/themes/neon-light.css";
import "./styles/themes/neon-dark.css";
import "./styles/themes/glass-light.css";
import "./styles/themes/glass-dark.css";
import "./styles/components/dashboard.css";
import "./styles/components/settings.css";

function App() {
  const { theme } = useThemeStore();
  const { language } = useI18nStore();
  const { fontSize } = useSettingsStore();

  // Apply theme on mount and detect system preference
  useEffect(() => {
    const mediaQuery = window.matchMedia("(prefers-color-scheme: dark)");
    const updateSystemTheme = () => {
      if (theme === "system") {
        document.documentElement.className = mediaQuery.matches
          ? "dark"
          : "light";
      } else {
        document.documentElement.className = theme;
      }
    };

    updateSystemTheme();
    mediaQuery.addEventListener("change", updateSystemTheme);
    return () => mediaQuery.removeEventListener("change", updateSystemTheme);
  }, [theme]);

  // Apply font size
  useEffect(() => {
    document.documentElement.style.fontSize = `${fontSize}%`;
  }, [fontSize]);

  return (
    <main className="app-container">
      <DashboardWidget />

      <aside className="settings-panel">
        <h2>Settings</h2>
        <LanguageSwitcher />
        <ThemeSwitcher />
        <ColorCustomizer />
        <ProgressBarPicker />
        <FontSizeSlider />
      </aside>
    </main>
  );
}

export default App;
```

### Step 18: Create Settings CSS

**styles/components/settings.css:**

```css
.settings-panel {
  padding: 16px;
  background: var(--bg-secondary);
  border-radius: 8px;
  margin-top: 16px;
}

.settings-panel > * + * {
  margin-top: 16px;
}

.theme-switcher,
.language-switcher {
  display: flex;
  align-items: center;
  gap: 8px;
}

.theme-switcher select,
.language-switcher select {
  background: var(--bg-primary);
  color: var(--text-primary);
  border: 1px solid var(--glass-border);
  padding: 6px 12px;
  border-radius: 4px;
  cursor: pointer;
}

.color-customizer {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.color-level-selector {
  display: flex;
  gap: 8px;
}

.color-level-selector button {
  flex: 1;
  padding: 6px 12px;
  background: var(--bg-primary);
  color: var(--text-primary);
  border: 1px solid var(--glass-border);
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.color-level-selector button.active {
  background: var(--accent);
  color: var(--bg-primary);
  border-color: var(--accent);
}

.accent-picker,
.full-customization {
  display: flex;
  flex-direction: column;
  gap: 8px;
  padding: 8px;
  background: var(--bg-primary);
  border-radius: 4px;
}

.color-input {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.color-input input[type="color"] {
  width: 60px;
  height: 30px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.progress-bar-picker {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.type-buttons {
  display: flex;
  gap: 8px;
}

.type-buttons button {
  flex: 1;
  padding: 6px 12px;
  background: var(--bg-primary);
  color: var(--text-primary);
  border: 1px solid var(--glass-border);
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.type-buttons button.active {
  background: var(--accent);
  color: var(--bg-primary);
  border-color: var(--accent);
}

.font-size-slider {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.font-size-slider input[type="range"] {
  width: 100%;
}

.range-labels {
  display: flex;
  justify-content: space-between;
  font-size: 12px;
  opacity: 0.7;
}

.focus-mode-indicator {
  display: inline-block;
}

.focus-toggle {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 6px 12px;
  background: var(--bg-secondary);
  color: var(--text-primary);
  border: 1px solid var(--glass-border);
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.focus-mode-indicator.active .focus-toggle {
  background: var(--accent);
  color: var(--bg-primary);
  border-color: var(--accent);
}

.goals-widget {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.goals-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.pace {
  font-weight: bold;
  font-size: 14px;
}

.budget-bar-container {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.budget-bar {
  height: 12px;
  background: rgba(0, 0, 0, 0.2);
  border-radius: 6px;
  overflow: hidden;
}

.budget-fill {
  height: 100%;
  transition: width 0.3s ease;
  border-radius: 6px;
}

.budget-text {
  display: flex;
  justify-content: center;
  gap: 4px;
  font-size: 14px;
}

.budget-text .current {
  font-weight: bold;
  color: var(--accent);
}

.dashboard-grid {
  margin-top: 16px;
}

.grid-item {
  cursor: move;
}

.drag-handle {
  cursor: move;
}

.progress-circular-wrapper,
.progress-gauge-wrapper {
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 16px;
}
```

## Todo List

- [ ] Install dependencies: react-grid-layout, react-i18next, i18next
- [ ] Create i18n setup with en.json + vi.json
- [ ] Create `stores/settings-store.ts` (fontSize, progressBarType, layout)
- [ ] Create `stores/theme-store.ts` (theme, colorLevel, accentColor, customColors)
- [ ] Create `stores/i18n-store.ts` (language)
- [ ] Create `styles/globals.css` with CSS variables
- [ ] Create 6 theme CSS files (default: neon-dark)
- [ ] Create `GlassCard`, `CircularProgress`, `GaugeProgress` UI components
- [ ] Create `UsageDisplay` with 3 progress bar variants
- [ ] Create `ResetCountdown` with dual format (HH:MM:SS + human readable)
- [ ] Create `GoalsWidget` with budget bar + pace indicator
- [ ] Create `FocusModeIndicator` with status toggle
- [ ] Create `GridLayoutWrapper` with drag-drop
- [ ] Create `ThemeSwitcher`, `ColorCustomizer`, `ProgressBarPicker`, `FontSizeSlider`, `LanguageSwitcher`
- [ ] Create `use-countdown.ts` hook with humanReadable
- [ ] Create `use-grid-layout.ts` hook
- [ ] Create `DashboardWidget` with grid layout
- [ ] Create `settings.css` component styles
- [ ] Update `App.tsx` with theme detection + settings panel
- [ ] Test all 6 themes visually (default: neon-dark)
- [ ] Test drag-drop layout persistence
- [ ] Test 3 progress bar variants
- [ ] Test color customization (3 levels)
- [ ] Test font size slider (80%-150%)
- [ ] Test i18n switching (en ↔ vi)

## Success Criteria

- All 6 themes display correctly (default: neon-dark)
- Progress bar has 3 working variants (linear/circular/gauge)
- Countdown shows dual format (HH:MM:SS + human readable)
- Color customization works at 3 levels (basic/advanced/expert)
- Dashboard layout is draggable and persists
- Font size slider works (80%-150%)
- i18n switches between English and Vietnamese
- Goals widget shows budget bar + pace indicator
- Focus mode indicator toggles correctly
- Theme/layout/settings persist after refresh (localStorage)
- Smooth 0.3s transitions between themes
- WCAG AA contrast on all themes

## Risk Assessment

| Risk                          | Mitigation                             |
| ----------------------------- | -------------------------------------- |
| backdrop-filter not supported | Fallback to solid background           |
| Neon too bright               | Reduce glow intensity on light themes  |
| Theme flicker on load         | Use CSS `:root` defaults               |
| Grid layout performance       | Limit max widgets to 8, debounce saves |
| i18n missing translations     | Fallback to English, add dev warnings  |
| Color picker browser compat   | Provide hex input fallback             |
| Circular/gauge rendering perf | Use CSS transforms over repaints       |

## Security Considerations

- No user data stored in themes/settings
- localStorage only stores: theme preference, layout positions, fontSize, language
- CSS-only styling, no JS injection risks
- Color picker values sanitized before CSS var injection

## Next Steps

- Phase 4: System Tray Integration (depends on usage display)
- Phase 5: Reminders & Notifications (depends on countdown)
- Phase 6: Settings Persistence (merge with current settings store)
