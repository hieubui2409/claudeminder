---
title: "Glassmorphism UI Redesign"
description: "Full frontend redesign with glassmorphism theme for claudiminder app"
status: pending
priority: P1
effort: 16h
branch: master
tags: [glassmorphism, ui-redesign, tauri, react]
created: 2026-01-17
---

# Glassmorphism UI Redesign Plan

## Overview

Complete frontend redesign replacing existing CSS/components with modern glassmorphism aesthetic. Optimized for 400x600px Tauri window.

## Dependency Graph

```
Phase 1 (Foundation)
    │
    ├──► Phase 2 (UI Components) ──┐
    │                               │
    └──► Phase 3 (Widgets) ────────┼──► Phase 4 (Layout) ──► Phase 5 (Polish)
                                   │
                                   │
```

**Parallel Execution:**

- Phase 2 + Phase 3 can run simultaneously (no file overlap)
- Phase 4 depends on Phase 1-3 completion
- Phase 5 is final integration

## Execution Strategy

| Phase | Name                     | Effort | Parallel | Depends On  |
| ----- | ------------------------ | ------ | -------- | ----------- |
| 1     | Design System Foundation | 2h     | -        | -           |
| 2     | UI Components            | 4h     | Yes      | Phase 1     |
| 3     | Dashboard Widgets        | 4h     | Yes      | Phase 1     |
| 4     | App Layout & Settings    | 4h     | No       | Phase 1,2,3 |
| 5     | Polish & Integration     | 2h     | No       | Phase 4     |

## File Ownership Matrix (NO OVERLAP)

| Phase | Files Owned                                                                   |
| ----- | ----------------------------------------------------------------------------- |
| 1     | `globals.css`, `index.css`, `themes/*.css`                                    |
| 2     | `components/ui/*.tsx`, `components/ui/*.module.css`                           |
| 3     | `components/dashboard/*.tsx`, `components/dashboard/*.module.css`             |
| 4     | `App.tsx`, `main.tsx`, `components/settings/*`, `hooks/use-theme.ts` (extend) |
| 5     | Integration tests, animation polish, final CSS tweaks in owned files          |

## Design Tokens

```css
/* Light Mode */
--glass-bg: rgba(255, 255, 255, 0.15);
--glass-border: rgba(255, 255, 255, 0.2);
--glass-blur: blur(12px);
--neon-accent: #00d4ff;
--text-primary: #1a1a2e;

/* Dark Mode */
--glass-bg-dark: rgba(0, 0, 0, 0.2);
--glass-border-dark: rgba(255, 255, 255, 0.1);
--neon-accent-dark: #00ffcc;
--text-primary-dark: #f0f0f0;
```

## Phases

- [phase-01-design-system.md](./phase-01-design-system.md) - CSS variables, themes, reset
- [phase-02-ui-components.md](./phase-02-ui-components.md) - GlassCard, buttons, inputs
- [phase-03-dashboard-widgets.md](./phase-03-dashboard-widgets.md) - Progress, countdown, goals
- [phase-04-app-layout.md](./phase-04-app-layout.md) - App shell, settings, routing
- [phase-05-polish-integration.md](./phase-05-polish-integration.md) - Final touches, testing

## Success Criteria

- [ ] All components render with glassmorphism effect
- [ ] Dark/Light theme switching works
- [ ] WCAG 4.5:1 text contrast met
- [ ] Animations smooth (60fps)
- [ ] 400x600px layout fits without scroll
- [ ] No CSS file ownership conflicts between phases

## Risk Mitigation

| Risk                    | Mitigation                                        |
| ----------------------- | ------------------------------------------------- |
| backdrop-filter support | Fallback solid bg for unsupported browsers        |
| Animation performance   | Use transform/opacity only, avoid layout triggers |
| File conflicts          | Strict file ownership, phase isolation            |
| Theme flicker           | CSS variables + prefers-color-scheme              |
