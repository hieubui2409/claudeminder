# React Dashboard Component Patterns Research

**Date:** 2026-01-17 | **Focus:** React 18+, Framer Motion, Zustand, Tauri v2

---

## 1. Component Architecture

### React 18+ Patterns for Small Dashboards (400x600px)

- **Hooks-first approach:** Replace class components entirely with functional components + hooks
- **Custom hooks for logic reuse:** Extract state, side effects into reusable hooks (e.g., `useOnlineStatus`, `useList`)
- **Composition over nesting:** Keep component tree shallow; compose via props rather than wrapper hell
- **React.memo for optimization:** Wrap components that don't need frequent re-renders
- **useTransition for responsive updates:** Handle async state updates without blocking UI (React 18+)

### Small Window Constraints (400x600px)

- Minimal nesting depth (max 3-4 levels)
- Single responsibility per component
- No virtualization needed (small list count)
- Responsive but fixed-aspect design
- Example structure: `Dashboard > [Stat Card, Usage Bar, Reminder Settings]`

### Code Pattern

```jsx
// Reusable custom hook for shared logic
const useUsageData = () => {
  const [data, setData] = useState(null);
  const [isPending, startTransition] = useTransition();

  useEffect(() => {
    startTransition(async () => {
      const result = await fetchUsage();
      setData(result);
    });
  }, []);

  return { data, isPending };
};

// Memoized component (prevent unnecessary re-renders)
const StatCard = React.memo(({ label, value }) => (
  <motion.div whileHover={{ scale: 1.02 }}>
    <div>
      {label}: {value}
    </div>
  </motion.div>
));
```

---

## 2. Animation Patterns (Framer Motion)

### Glass UI Hover Interactions

- **`whileHover` prop:** Simplest, declarative hover animations (cross-device safe, no sticky states on touch)
- **Gesture detection:** Motion filters emulated hover events on touch devices automatically
- **Smooth spring transitions:** Default spring physics feels natural without explicit duration tuning
- **Stagger on lists:** `variants` + `transition: { staggerChildren }` for sequential animations

### Common Glass UI Effects

```jsx
// Hover scale + shadow
<motion.div
  whileHover={{
    scale: 1.02,
    boxShadow: '0 20px 40px rgba(0,0,0,0.2)'
  }}
  transition={{ type: 'spring', stiffness: 300, damping: 30 }}
>
  Content
</motion.div>

// Backdrop blur + opacity transition
<motion.div
  animate={{ backdropFilter: 'blur(10px)', opacity: 0.9 }}
  exit={{ backdropFilter: 'blur(0px)', opacity: 0 }}
>
  Modal
</motion.div>

// Staggered list animations
<motion.ul variants={containerVariants} initial="hidden" animate="show">
  {items.map((item) => (
    <motion.li key={item.id} variants={itemVariants}>
      {item.text}
    </motion.li>
  ))}
</motion.ul>
```

### Animation Best Practices

- Avoid heavy animations in small windows (60fps target on low-end machines)
- Use `reduce-motion` media query for accessibility
- Keep animation duration 200-400ms for UI feedback
- Use Motion v0.20+ (faster, lighter than Framer Motion for small apps)

---

## 3. State Management (Zustand)

### Zustand Setup for Dashboard

- **Minimal boilerplate:** Single `create()` call for entire store
- **Hook-based API:** Components import & use store like native React hooks
- **Selective subscriptions:** Only re-render on specific state changes (automatic equality check)
- **No provider wrapper needed** (unless using Context for testing)

### Store Structure

```ts
// src/stores/useDashboardStore.ts
import { create } from 'zustand';

interface DashboardState {
  usage: number;
  resetTime: Date | null;
  reminderInterval: number;
  setUsage: (val: number) => void;
  setResetTime: (val: Date) => void;
  updateReminder: (interval: number) => void;
}

export const useDashboardStore = create<DashboardState>((set) => ({
  usage: 0,
  resetTime: null,
  reminderInterval: 3600,
  setUsage: (usage) => set({ usage }),
  setResetTime: (resetTime) => set({ resetTime }),
  updateReminder: (reminderInterval) => set({ reminderInterval }),
}));

// Component usage - automatic re-render only on used selectors
const UsageDisplay = () => {
  const usage = useDashboardStore((state) => state.usage);
  const setUsage = useDashboardStore((state) => state.setUsage);
  return <div>{usage}%</div>;
};
```

### Tauri Integration Pattern

```ts
// Connect Zustand to Tauri backend
useEffect(() => {
  const unsubscribe = listen("usage-updated", (event: { payload: number }) => {
    useDashboardStore.setState({ usage: event.payload });
  });
  return () => unsubscribe.then((f) => f());
}, []);

// Dispatch to Rust backend
const handleRefresh = async () => {
  const result = await invoke("get_usage_stats");
  useDashboardStore.setState(result);
};
```

---

## 4. CSS Organization

### Recommendation: CSS Modules

**Rationale for 400x600 dashboard:**

- ✅ No runtime CSS-in-JS overhead (scoped at build time)
- ✅ Prevent accidental global style pollution
- ✅ Type-safe with TypeScript (`import styles from './Card.module.css'`)
- ✅ Faster than vanilla CSS in large apps due to cascade simplification
- ⚠️ Marginally larger bundle (generated class names), negligible for small apps

### File Structure

```
src/components/
├── StatCard/
│   ├── StatCard.tsx
│   ├── StatCard.module.css
│   └── index.ts
├── UsageBar/
│   ├── UsageBar.tsx
│   ├── UsageBar.module.css
│   └── index.ts
└── ...
```

### CSS Modules Usage

```css
/* StatCard.module.css */
.container {
  backdrop-filter: blur(10px);
  background: rgba(255, 255, 255, 0.1);
  border-radius: 12px;
  padding: 16px;
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.container:hover {
  background: rgba(255, 255, 255, 0.15);
}
```

```tsx
// StatCard.tsx
import styles from "./StatCard.module.css";
import { motion } from "framer-motion";

export const StatCard = ({ label, value }) => (
  <motion.div className={styles.container} whileHover={{ scale: 1.02 }}>
    <p>{label}</p>
    <h3>{value}</h3>
  </motion.div>
);
```

---

## 5. Tauri v2 + React Integration

### Architecture Best Practices

- **Separation:** Rust in `src-tauri/`, React in `src/`
- **Communication:** `tauri::invoke()` (React→Rust), event system (Rust→React)
- **State:** Zustand for UI state, Tauri Manager + Mutex for backend state

### Tauri Command Example

```rust
// src-tauri/src/main.rs
use tauri::State;

#[derive(Default)]
pub struct AppState {
    pub usage: f64,
}

#[tauri::command]
fn get_usage_stats(state: State<'_, AppState>) -> f64 {
    state.usage
}

#[tauri::command]
async fn fetch_claude_usage() -> Result<f64, String> {
    // Call Anthropic API
    Ok(45.2)
}
```

### React Hook for Tauri Invocation

```ts
// src/hooks/useTauriInvoke.ts
import { invoke } from '@tauri-apps/api/core';
import { useState, useEffect } from 'react';

export const useTauriCommand = <T,>(command: string) => {
  const [data, setData] = useState<T | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    invoke<T>(command)
      .then(setData)
      .catch((err) => setError(err.toString()))
      .finally(() => setLoading(false));
  }, [command]);

  return { data, error, loading };
};

// Usage in component
const Dashboard = () => {
  const { data: usage, loading } = useTauriCommand<number>('get_usage_stats');
  return <div>{loading ? 'Loading...' : `${usage}%`}</div>;
};
```

### Event System (Rust→React)

```ts
// React listener
import { listen } from "@tauri-apps/api/event";

useEffect(() => {
  const unsubscribe = listen<number>("usage-update", (event) => {
    useDashboardStore.setState({ usage: event.payload });
  });

  return () => {
    unsubscribe.then((f) => f());
  };
}, []);
```

```rust
// Rust emitter
app.emit_all("usage-update", 42.5).unwrap();
```

---

## 6. Performance Checklist

| Item              | Strategy                                                 |
| ----------------- | -------------------------------------------------------- |
| **Re-renders**    | React.memo + Zustand selectors                           |
| **Animation FPS** | Motion library handles 60fps automatically               |
| **Bundle size**   | CSS Modules + tree-shaking (avoid runtime CSS-in-JS)     |
| **Tauri IPC**     | Batch commands, cache results in Zustand                 |
| **CSS scoping**   | CSS Modules prevent cascade overhead                     |
| **Small window**  | No virtualization, fixed layout, <5 top-level components |

---

## 7. Code Snippet: Minimal Dashboard

```tsx
// src/App.tsx
import { useEffect } from "react";
import { motion } from "framer-motion";
import { invoke } from "@tauri-apps/api/core";
import { listen } from "@tauri-apps/api/event";
import { useDashboardStore } from "./stores/useDashboardStore";
import { StatCard } from "./components/StatCard";
import styles from "./App.module.css";

export const App = () => {
  const usage = useDashboardStore((s) => s.usage);
  const setUsage = useDashboardStore((s) => s.setUsage);

  useEffect(() => {
    // Fetch initial usage
    invoke<number>("get_usage_stats").then(setUsage);

    // Listen for updates from Rust
    listen<number>("usage-update", (e) => setUsage(e.payload)).then((f) => f);
  }, [setUsage]);

  return (
    <motion.div
      className={styles.container}
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ duration: 0.3 }}
    >
      <h1>Claude Usage</h1>
      <StatCard label="Usage" value={`${usage.toFixed(1)}%`} />
      <motion.button
        className={styles.button}
        whileHover={{ scale: 1.05 }}
        whileTap={{ scale: 0.95 }}
      >
        Refresh
      </motion.button>
    </motion.div>
  );
};
```

---

## Key Takeaways

1. **Component architecture:** Hooks + custom hooks for reusability, React.memo for optimization
2. **Animations:** Framer Motion `whileHover` for glass UI, Motion library for lighter builds
3. **State:** Zustand with selective subscriptions, no context wrappers needed
4. **Styling:** CSS Modules for scoped, performant styles (no runtime overhead)
5. **Tauri integration:** `invoke()` for commands, event system for Rust→React updates, Zustand as single source of truth
6. **Small window advantage:** Simplicity wins; no virtualization, fixed layout, memoization handles everything

---

## Unresolved Questions

- Should we use Motion v0.20+ instead of Framer Motion for smaller bundle size? (Motion is newer, lighter, but less mature)
- Exact CSS Modules vs Tailwind trade-off for this specific use case? (Tailwind + Modules hybrid possible but adds complexity)
- Best practice for caching Anthropic API calls in Tauri backend? (In-memory vs persistent database)
