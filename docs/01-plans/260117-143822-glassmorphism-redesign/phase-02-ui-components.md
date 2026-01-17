---
phase: 2
title: "UI Components"
status: pending
effort: 4h
parallel: true
depends_on: [1]
parallel_with: [3]
---

# Phase 2: UI Components

## Parallelization Info

- **Can run parallel with:** Phase 3 (Dashboard Widgets)
- **Must wait for:** Phase 1 (Design System)
- **Estimated time:** 4h

## File Ownership (EXCLUSIVE)

```
src/frontend/src/components/ui/
├── GlassCard.tsx           ← CREATE
├── GlassCard.module.css    ← CREATE
├── Button.tsx              ← CREATE
├── Button.module.css       ← CREATE
├── Input.tsx               ← CREATE
├── Input.module.css        ← CREATE
├── Toggle.tsx              ← CREATE
├── Toggle.module.css       ← CREATE
├── Icon.tsx                ← CREATE
└── index.ts                ← CREATE (barrel export)
```

**CONFLICT PREVENTION:**

- Phase 3 owns `components/dashboard/*` - DO NOT touch
- Phase 4 owns `components/settings/*` - DO NOT touch

## Overview

Build reusable glassmorphism UI primitives that other phases will consume.

## Components Specification

### 1. GlassCard

Base container with glassmorphism effect.

```tsx
// Props
interface GlassCardProps {
  children: React.ReactNode;
  className?: string;
  padding?: "none" | "sm" | "md" | "lg";
  hover?: boolean; // Enable hover glow effect
  animate?: boolean; // Fade-in animation
}
```

**CSS Module:**

```css
.card {
  background: var(--glass-bg);
  backdrop-filter: blur(var(--glass-blur));
  -webkit-backdrop-filter: blur(var(--glass-blur));
  border: 1px solid var(--glass-border);
  border-radius: var(--radius-md);
  transition: var(--transition-normal);
}

.hover:hover {
  box-shadow: var(--shadow-glow);
  border-color: var(--neon-accent);
}

.paddingNone {
  padding: 0;
}
.paddingSm {
  padding: var(--space-sm);
}
.paddingMd {
  padding: var(--space-md);
}
.paddingLg {
  padding: var(--space-lg);
}
```

### 2. Button

Glassmorphism button with variants.

```tsx
interface ButtonProps {
  children: React.ReactNode;
  variant?: "primary" | "secondary" | "ghost";
  size?: "sm" | "md" | "lg";
  disabled?: boolean;
  loading?: boolean;
  onClick?: () => void;
  className?: string;
}
```

**CSS Module:**

```css
.button {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: var(--space-xs);
  font-family: var(--font-family);
  font-weight: var(--font-weight-medium);
  border-radius: var(--radius-md);
  cursor: pointer;
  transition: var(--transition-fast);
}

.primary {
  background: var(--neon-accent);
  color: var(--text-inverse);
  border: none;
}

.primary:hover:not(:disabled) {
  background: var(--neon-accent-hover);
  box-shadow: var(--shadow-glow);
}

.secondary {
  background: var(--glass-bg);
  backdrop-filter: blur(var(--glass-blur));
  color: var(--text-primary);
  border: 1px solid var(--glass-border);
}

.ghost {
  background: transparent;
  color: var(--text-primary);
  border: none;
}

.ghost:hover {
  background: var(--glass-bg);
}

.sizeSm {
  height: 28px;
  padding: 0 var(--space-sm);
  font-size: var(--font-size-xs);
}

.sizeMd {
  height: 36px;
  padding: 0 var(--space-md);
  font-size: var(--font-size-sm);
}

.sizeLg {
  height: 44px;
  padding: 0 var(--space-lg);
  font-size: var(--font-size-md);
}

.disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.loading {
  pointer-events: none;
}
```

### 3. Input

Text input with glassmorphism style.

```tsx
interface InputProps {
  value: string;
  onChange: (value: string) => void;
  placeholder?: string;
  type?: "text" | "number" | "password";
  disabled?: boolean;
  error?: string;
  label?: string;
}
```

**CSS Module:**

```css
.wrapper {
  display: flex;
  flex-direction: column;
  gap: var(--space-xs);
}

.label {
  font-size: var(--font-size-sm);
  color: var(--text-secondary);
  font-weight: var(--font-weight-medium);
}

.input {
  width: 100%;
  height: 40px;
  padding: 0 var(--space-md);
  background: var(--glass-bg);
  backdrop-filter: blur(var(--glass-blur));
  border: 1px solid var(--glass-border);
  border-radius: var(--radius-md);
  color: var(--text-primary);
  font-size: var(--font-size-md);
  transition: var(--transition-fast);
}

.input:focus {
  border-color: var(--neon-accent);
  box-shadow: var(--focus-ring);
}

.input::placeholder {
  color: var(--text-muted);
}

.error {
  border-color: var(--accent-error);
}

.errorText {
  font-size: var(--font-size-xs);
  color: var(--accent-error);
}
```

### 4. Toggle

On/off toggle switch.

```tsx
interface ToggleProps {
  checked: boolean;
  onChange: (checked: boolean) => void;
  label?: string;
  disabled?: boolean;
  size?: "sm" | "md";
}
```

**CSS Module:**

```css
.wrapper {
  display: inline-flex;
  align-items: center;
  gap: var(--space-sm);
}

.track {
  position: relative;
  border-radius: var(--radius-full);
  background: var(--glass-bg);
  border: 1px solid var(--glass-border);
  cursor: pointer;
  transition: var(--transition-fast);
}

.sizeSm .track {
  width: 36px;
  height: 20px;
}

.sizeMd .track {
  width: 44px;
  height: 24px;
}

.thumb {
  position: absolute;
  top: 2px;
  left: 2px;
  background: var(--text-muted);
  border-radius: 50%;
  transition: var(--transition-fast);
}

.sizeSm .thumb {
  width: 14px;
  height: 14px;
}

.sizeMd .thumb {
  width: 18px;
  height: 18px;
}

.checked .track {
  background: var(--neon-accent);
  border-color: var(--neon-accent);
}

.checked .thumb {
  background: white;
  transform: translateX(16px);
}

.sizeSm.checked .thumb {
  transform: translateX(16px);
}

.sizeMd.checked .thumb {
  transform: translateX(20px);
}

.label {
  font-size: var(--font-size-sm);
  color: var(--text-primary);
}

.disabled {
  opacity: 0.5;
  pointer-events: none;
}
```

### 5. Icon

SVG icon wrapper with size variants.

```tsx
interface IconProps {
  name:
    | "settings"
    | "sun"
    | "moon"
    | "check"
    | "x"
    | "refresh"
    | "target"
    | "clock";
  size?: "sm" | "md" | "lg";
  className?: string;
}
```

Inline SVG icons for: settings, sun, moon, check, x, refresh, target, clock

## Implementation Steps

1. Create folder structure: `mkdir -p src/frontend/src/components/ui`
2. Implement GlassCard.tsx + GlassCard.module.css
3. Implement Button.tsx + Button.module.css
4. Implement Input.tsx + Input.module.css
5. Implement Toggle.tsx + Toggle.module.css
6. Implement Icon.tsx (no CSS module needed)
7. Create index.ts barrel export

## Barrel Export

```tsx
// src/frontend/src/components/ui/index.ts
export { GlassCard } from "./GlassCard";
export { Button } from "./Button";
export { Input } from "./Input";
export { Toggle } from "./Toggle";
export { Icon } from "./Icon";
```

## Success Criteria

- [ ] All 5 components implemented with TypeScript
- [ ] CSS Modules properly scoped
- [ ] Components consume Phase 1 CSS variables
- [ ] Hover/focus states work correctly
- [ ] Dark/light theme support via CSS variables
- [ ] No TypeScript errors
- [ ] Barrel export working

## Conflict Prevention

1. **DO NOT** import from `components/dashboard/*` (Phase 3 owns)
2. **DO NOT** create settings components (Phase 4 owns)
3. **DO NOT** modify any files from Phase 1
4. **DO NOT** create App.tsx or main.tsx (Phase 4 owns)

## Testing Checklist

```bash
# Type check
npx tsc --noEmit

# Component exists
ls -la src/frontend/src/components/ui/
```

## Notes for Parallel Execution

When running with Phase 3:

- Communicate via shared CSS variables from Phase 1
- No direct component imports between Phase 2 and 3
- Phase 4 will wire everything together
