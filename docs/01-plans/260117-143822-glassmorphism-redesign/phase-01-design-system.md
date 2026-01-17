---
phase: 1
title: "Design System Foundation"
status: pending
effort: 2h
parallel: false
depends_on: []
---

# Phase 1: Design System Foundation

## Parallelization Info

- **Can run parallel with:** None (foundation phase)
- **Must complete before:** Phase 2, Phase 3, Phase 4, Phase 5
- **Estimated time:** 2h

## File Ownership (EXCLUSIVE)

```
src/frontend/src/styles/
├── globals.css          ← CREATE
├── index.css            ← CREATE
├── variables.css        ← CREATE
└── themes/
    ├── light.css        ← CREATE
    └── dark.css         ← CREATE
```

**CONFLICT PREVENTION:** These files are ONLY modified in Phase 1. Other phases import but DO NOT edit.

## Overview

Establish CSS design tokens, glassmorphism variables, reset styles, and theme structure.

## Key Design Decisions

1. **CSS Variables over Tailwind** - Direct control for glass effects
2. **CSS Modules** - Scoped styles, no conflicts
3. **prefers-color-scheme** - System theme detection
4. **Layer cascade** - @layer for specificity control

## Implementation Steps

### Step 1: Create variables.css

```css
/* src/frontend/src/styles/variables.css */
:root {
  /* Glass Effects */
  --glass-blur: 12px;
  --glass-bg-opacity: 0.15;
  --glass-border-opacity: 0.2;

  /* Sizing */
  --window-width: 400px;
  --window-height: 600px;
  --radius-sm: 8px;
  --radius-md: 12px;
  --radius-lg: 16px;
  --radius-full: 9999px;

  /* Spacing */
  --space-xs: 4px;
  --space-sm: 8px;
  --space-md: 16px;
  --space-lg: 24px;
  --space-xl: 32px;

  /* Typography */
  --font-family: "Inter", -apple-system, BlinkMacSystemFont, sans-serif;
  --font-size-xs: 11px;
  --font-size-sm: 13px;
  --font-size-md: 15px;
  --font-size-lg: 18px;
  --font-size-xl: 24px;
  --font-size-2xl: 32px;
  --font-weight-normal: 400;
  --font-weight-medium: 500;
  --font-weight-semibold: 600;
  --font-weight-bold: 700;

  /* Transitions */
  --transition-fast: 150ms ease;
  --transition-normal: 250ms ease;
  --transition-slow: 400ms ease;

  /* Shadows */
  --shadow-sm: 0 2px 8px rgba(0, 0, 0, 0.1);
  --shadow-md: 0 4px 16px rgba(0, 0, 0, 0.15);
  --shadow-lg: 0 8px 32px rgba(0, 0, 0, 0.2);
  --shadow-glow: 0 0 20px var(--neon-accent);
}
```

### Step 2: Create light.css

```css
/* src/frontend/src/styles/themes/light.css */
[data-theme="light"] {
  /* Backgrounds */
  --bg-primary: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  --bg-secondary: #f8f9fa;
  --glass-bg: rgba(255, 255, 255, 0.15);
  --glass-border: rgba(255, 255, 255, 0.2);

  /* Text - WCAG 4.5:1 compliant */
  --text-primary: #1a1a2e;
  --text-secondary: #4a4a68;
  --text-muted: #6b6b8a;
  --text-inverse: #ffffff;

  /* Accents */
  --neon-accent: #00d4ff;
  --neon-accent-hover: #00b8e6;
  --accent-success: #10b981;
  --accent-warning: #f59e0b;
  --accent-error: #ef4444;

  /* Semantic */
  --border-color: rgba(255, 255, 255, 0.25);
  --focus-ring: 0 0 0 2px var(--neon-accent);
}
```

### Step 3: Create dark.css

```css
/* src/frontend/src/styles/themes/dark.css */
[data-theme="dark"] {
  /* Backgrounds */
  --bg-primary: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
  --bg-secondary: #0f0f1a;
  --glass-bg: rgba(0, 0, 0, 0.25);
  --glass-border: rgba(255, 255, 255, 0.1);

  /* Text - WCAG 4.5:1 compliant */
  --text-primary: #f0f0f0;
  --text-secondary: #b8b8c8;
  --text-muted: #7a7a8a;
  --text-inverse: #1a1a2e;

  /* Accents */
  --neon-accent: #00ffcc;
  --neon-accent-hover: #00e6b8;
  --accent-success: #34d399;
  --accent-warning: #fbbf24;
  --accent-error: #f87171;

  /* Semantic */
  --border-color: rgba(255, 255, 255, 0.08);
  --focus-ring: 0 0 0 2px var(--neon-accent);
}
```

### Step 4: Create globals.css

```css
/* src/frontend/src/styles/globals.css */
@import "./variables.css";
@import "./themes/light.css";
@import "./themes/dark.css";

/* Reset */
*,
*::before,
*::after {
  box-sizing: border-box;
  margin: 0;
  padding: 0;
}

html {
  font-size: 16px;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

body {
  font-family: var(--font-family);
  font-size: var(--font-size-md);
  color: var(--text-primary);
  background: var(--bg-primary);
  line-height: 1.5;
  overflow: hidden;
}

/* Focus visible for accessibility */
:focus-visible {
  outline: none;
  box-shadow: var(--focus-ring);
}

/* Scrollbar styling */
::-webkit-scrollbar {
  width: 6px;
}

::-webkit-scrollbar-track {
  background: transparent;
}

::-webkit-scrollbar-thumb {
  background: var(--glass-border);
  border-radius: var(--radius-full);
}

/* Selection */
::selection {
  background: var(--neon-accent);
  color: var(--text-inverse);
}

/* System theme detection */
@media (prefers-color-scheme: dark) {
  :root:not([data-theme]) {
    /* Apply dark theme variables */
  }
}
```

### Step 5: Create index.css

```css
/* src/frontend/src/styles/index.css */
@import "./globals.css";

/* App container */
#root {
  width: var(--window-width);
  height: var(--window-height);
  overflow: hidden;
  position: relative;
}

/* Glass utilities - can be composed */
.glass {
  background: var(--glass-bg);
  backdrop-filter: blur(var(--glass-blur));
  -webkit-backdrop-filter: blur(var(--glass-blur));
  border: 1px solid var(--glass-border);
  border-radius: var(--radius-md);
}

/* Fallback for unsupported browsers */
@supports not (backdrop-filter: blur(1px)) {
  .glass {
    background: var(--bg-secondary);
  }
}

/* Animation utilities */
.animate-fade-in {
  animation: fadeIn var(--transition-normal) forwards;
}

.animate-slide-up {
  animation: slideUp var(--transition-normal) forwards;
}

@keyframes fadeIn {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}

@keyframes slideUp {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
```

## Directory Structure After Phase 1

```
src/frontend/src/styles/
├── globals.css       ✅
├── index.css         ✅
├── variables.css     ✅
└── themes/
    ├── light.css     ✅
    └── dark.css      ✅
```

## Success Criteria

- [ ] All CSS variables defined and documented
- [ ] Light/dark themes switchable via `data-theme` attribute
- [ ] Glass utility class works with backdrop-filter
- [ ] Fallback styles for unsupported browsers
- [ ] No CSS errors in browser console
- [ ] Typography scale visible and consistent

## Conflict Prevention

1. **DO NOT** create component-specific styles in this phase
2. **DO NOT** modify any TSX files
3. **DO NOT** touch files in `components/` folder
4. All theme variables must be defined here - other phases only consume

## Testing Checklist

```bash
# Verify files created
ls -la src/frontend/src/styles/
ls -la src/frontend/src/styles/themes/

# Check CSS syntax
npx stylelint "src/frontend/src/styles/**/*.css"
```

## Next Steps

After completion, Phase 2 and Phase 3 can start **in parallel**.
