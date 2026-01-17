---
phase: 4
title: "App Layout & Settings"
status: pending
effort: 4h
parallel: false
depends_on: [1, 2, 3]
---

# Phase 4: App Layout & Settings

## Parallelization Info

- **Can run parallel with:** None
- **Must wait for:** Phase 1, Phase 2, Phase 3
- **Estimated time:** 4h

## File Ownership (EXCLUSIVE)

```
src/frontend/src/
├── App.tsx                           ← CREATE
├── main.tsx                          ← CREATE
├── components/settings/
│   ├── SettingsPanel.tsx             ← CREATE
│   ├── SettingsPanel.module.css      ← CREATE
│   ├── ThemeSwitcher.tsx             ← CREATE
│   ├── ThemeSwitcher.module.css      ← CREATE
│   ├── ReminderConfig.tsx            ← CREATE
│   ├── ReminderConfig.module.css     ← CREATE
│   ├── FocusModeToggle.tsx           ← CREATE
│   ├── FocusModeToggle.module.css    ← CREATE
│   └── index.ts                      ← CREATE
├── hooks/
│   └── use-theme.ts                  ← EXTEND (add glassmorphism logic)
└── types/
    └── settings.ts                   ← CREATE (if needed)
```

**CONFLICT PREVENTION:**

- Phase 2 owns `components/ui/*` - IMPORT ONLY, DO NOT modify
- Phase 3 owns `components/dashboard/*` - IMPORT ONLY, DO NOT modify

## Overview

Wire all components together: App shell, navigation, settings drawer, theme system.

## App Structure

```
┌─────────────────────────────────┐
│  Header (compact countdown)     │ 48px
├─────────────────────────────────┤
│                                 │
│  Main Content                   │
│  - CircularProgress (center)    │
│  - ResetCountdown               │
│  - GoalsIndicator               │
│  - UsageStats                   │
│                                 │ 472px
├─────────────────────────────────┤
│  Footer (settings, theme)       │ 80px
└─────────────────────────────────┘
        400px x 600px

SettingsPanel: Slide-in drawer from right
```

## Components Specification

### 1. App.tsx

Main application shell.

```tsx
// App.tsx structure
function App() {
  const [settingsOpen, setSettingsOpen] = useState(false);
  const { theme } = useTheme();
  const { usage, resetTime, goals } = useUsage();

  return (
    <div className={styles.app} data-theme={theme}>
      <Header onSettingsClick={() => setSettingsOpen(true)} />
      <main className={styles.main}>
        <CircularProgress value={usage.percentage} size="lg" />
        <ResetCountdown resetTime={resetTime} />
        <GoalsIndicator
          current={goals.current}
          goal={goals.target}
          period="daily"
        />
        <UsageStats stats={usage.stats} />
      </main>
      <Footer>
        <FocusModeToggle />
        <ThemeSwitcher />
      </Footer>
      <SettingsPanel
        open={settingsOpen}
        onClose={() => setSettingsOpen(false)}
      />
    </div>
  );
}
```

**CSS Module (App.module.css):**

```css
.app {
  width: var(--window-width);
  height: var(--window-height);
  display: flex;
  flex-direction: column;
  background: var(--bg-primary);
  overflow: hidden;
}

.header {
  height: 48px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 var(--space-md);
  background: var(--glass-bg);
  backdrop-filter: blur(var(--glass-blur));
  border-bottom: 1px solid var(--glass-border);
}

.main {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: var(--space-lg);
  padding: var(--space-md);
}

.footer {
  height: 80px;
  display: flex;
  align-items: center;
  justify-content: space-around;
  padding: 0 var(--space-md);
  background: var(--glass-bg);
  backdrop-filter: blur(var(--glass-blur));
  border-top: 1px solid var(--glass-border);
}
```

### 2. main.tsx

Entry point with providers.

```tsx
import React from "react";
import ReactDOM from "react-dom/client";
import { App } from "./App";
import "./styles/index.css";

ReactDOM.createRoot(document.getElementById("root")!).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
);
```

### 3. SettingsPanel

Slide-in drawer from right edge.

```tsx
interface SettingsPanelProps {
  open: boolean;
  onClose: () => void;
}
```

**Features:**

- Slide animation with Framer Motion
- Backdrop overlay with blur
- Close on backdrop click or escape key
- Settings sections: Reminders, Goals, Theme, About

**CSS Module:**

```css
.overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.4);
  backdrop-filter: blur(4px);
  z-index: 100;
}

.panel {
  position: fixed;
  top: 0;
  right: 0;
  bottom: 0;
  width: 320px;
  background: var(--bg-secondary);
  border-left: 1px solid var(--glass-border);
  z-index: 101;
  overflow-y: auto;
  padding: var(--space-lg);
}

.header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: var(--space-lg);
}

.title {
  font-size: var(--font-size-lg);
  font-weight: var(--font-weight-semibold);
  color: var(--text-primary);
}

.closeButton {
  background: none;
  border: none;
  color: var(--text-secondary);
  cursor: pointer;
  padding: var(--space-xs);
}

.section {
  margin-bottom: var(--space-lg);
}

.sectionTitle {
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-medium);
  color: var(--text-secondary);
  text-transform: uppercase;
  letter-spacing: 0.5px;
  margin-bottom: var(--space-sm);
}
```

### 4. ThemeSwitcher

Dark/light toggle with sun/moon icons.

```tsx
function ThemeSwitcher() {
  const { theme, setTheme } = useTheme();

  return (
    <button onClick={() => setTheme(theme === "dark" ? "light" : "dark")}>
      <Icon name={theme === "dark" ? "sun" : "moon"} />
    </button>
  );
}
```

**CSS Module:**

```css
.button {
  width: 44px;
  height: 44px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--glass-bg);
  backdrop-filter: blur(var(--glass-blur));
  border: 1px solid var(--glass-border);
  border-radius: var(--radius-full);
  cursor: pointer;
  transition: var(--transition-fast);
}

.button:hover {
  border-color: var(--neon-accent);
  box-shadow: var(--shadow-glow);
}

.icon {
  color: var(--text-primary);
  transition: var(--transition-fast);
}
```

### 5. FocusModeToggle

Pill-shaped toggle for focus mode.

```tsx
interface FocusModeToggleProps {
  className?: string;
}

function FocusModeToggle({ className }: FocusModeToggleProps) {
  const { focusMode, setFocusMode } = useSettings();

  return (
    <button
      className={clsx(styles.toggle, focusMode && styles.active, className)}
      onClick={() => setFocusMode(!focusMode)}
    >
      <Icon name="target" size="sm" />
      <span>Focus</span>
    </button>
  );
}
```

**CSS Module:**

```css
.toggle {
  display: inline-flex;
  align-items: center;
  gap: var(--space-xs);
  height: 36px;
  padding: 0 var(--space-md);
  background: var(--glass-bg);
  backdrop-filter: blur(var(--glass-blur));
  border: 1px solid var(--glass-border);
  border-radius: var(--radius-full);
  color: var(--text-secondary);
  font-size: var(--font-size-sm);
  cursor: pointer;
  transition: var(--transition-fast);
}

.toggle:hover {
  border-color: var(--neon-accent);
}

.active {
  background: var(--neon-accent);
  border-color: var(--neon-accent);
  color: var(--text-inverse);
  box-shadow: var(--shadow-glow);
}
```

### 6. ReminderConfig

Reminder settings component.

```tsx
interface ReminderConfigProps {
  config: ReminderSettings;
  onChange: (config: ReminderSettings) => void;
}

// Presets: before_reset, on_reset, custom
```

**Features:**

- Radio buttons for preset strategies
- Custom interval input (minutes)
- Enable/disable toggle

## Implementation Steps

1. Create `mkdir -p src/frontend/src/components/settings`
2. Extend use-theme.ts to handle data-theme attribute
3. Implement App.tsx with layout structure
4. Implement main.tsx with providers
5. Implement SettingsPanel with Framer Motion
6. Implement ThemeSwitcher
7. Implement FocusModeToggle
8. Implement ReminderConfig
9. Create settings/index.ts barrel export
10. Wire all imports and test integration

## Hooks Extension

### use-theme.ts (extend)

```tsx
// Add to existing hook
export function useTheme() {
  const [theme, setThemeState] = useState<"light" | "dark">(() => {
    const stored = localStorage.getItem("theme");
    if (stored) return stored as "light" | "dark";
    return window.matchMedia("(prefers-color-scheme: dark)").matches
      ? "dark"
      : "light";
  });

  useEffect(() => {
    document.documentElement.setAttribute("data-theme", theme);
    localStorage.setItem("theme", theme);
  }, [theme]);

  return { theme, setTheme: setThemeState };
}
```

## Dependencies

```json
{
  "framer-motion": "^11.x",
  "clsx": "^2.x"
}
```

## Success Criteria

- [ ] App renders with correct 400x600 layout
- [ ] Theme switching works (dark/light)
- [ ] Settings panel slides in/out smoothly
- [ ] All Phase 2 components imported and working
- [ ] All Phase 3 widgets imported and working
- [ ] Focus mode toggle persists state
- [ ] Reminder config saves settings
- [ ] No layout overflow/scroll

## Conflict Prevention

1. **DO NOT** modify any files from Phase 1, 2, or 3
2. **ONLY** import components, do not edit them
3. If Phase 2/3 components need changes, document for Phase 5

## Testing Checklist

```bash
# Type check
npx tsc --noEmit

# Dev server
bun run tauri dev

# Check console for errors
```

## Integration Notes

Phase 4 is the integration phase - it composes:

- CSS from Phase 1
- UI primitives from Phase 2
- Dashboard widgets from Phase 3

Any issues found should be documented for Phase 5 fixes.
