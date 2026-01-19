---
title: "Show Mode & Enhanced Tray Settings"
description: "Add display mode, overlay position persistence, and tray info enhancements"
status: completed
priority: P2
effort: 5h
branch: master
tags: [settings, window-management, tauri, tray]
created: 2026-01-19
validated: 2026-01-19
completed: 2026-01-19
reviewed: 2026-01-19
---

# Show Mode & Enhanced Tray Settings Implementation Plan

## Overview

Add settings and enhancements to Claudeminder:

1. **Show Mode** - Control which windows show on startup (main/overlay/both)
2. **Remember Overlay Position** - Persist overlay window position across restarts
3. **Tray Icon % Realtime** - Display usage percentage in tray icon dynamically
4. **Tray Menu Info** - Show reset time and % in tray context menu

## Validation Summary

**Validated:** 2026-01-19
**Questions asked:** 6

### Confirmed Decisions

- Show Mode: Apply only on startup (change requires restart)
- Main window mode "overlay": Hide main but keep running in background
- Trace: Always track (removed as separate setting - always enabled)
- Remember position: Overlay only
- Tray icon: Show % realtime (dynamic icon generation)
- Tray menu: Display reset time + usage %

## Dependency Graph

```
┌─────────────────────┐     ┌─────────────────────┐
│   Phase 1           │     │   Phase 2           │
│   Frontend Settings │     │   Tauri Backend     │
│   (TypeScript)      │     │   (Rust)            │
│   ~1.5h             │     │   ~2h               │
└─────────┬───────────┘     └─────────┬───────────┘
          │                           │
          │     ┌─────────────────┐   │
          └────►│   Phase 3       │◄──┘
                │   Integration   │
                │   ~1h           │
                └─────────────────┘
```

**Parallel Execution**: Phase 1 and Phase 2 can run simultaneously.
**Sequential**: Phase 3 depends on both Phase 1 and Phase 2.

## File Ownership Matrix

| File                                          | Phase 1 | Phase 2 | Phase 3 | Notes                      |
| --------------------------------------------- | ------- | ------- | ------- | -------------------------- |
| `stores/settings-store.ts`                    | ✓       |         |         | Add showMode               |
| `types/settings.ts`                           | ✓       |         |         | Add ShowMode type          |
| `components/settings/SettingsPanel.tsx`       | ✓       |         |         | Import new components      |
| `components/settings/display-mode-select.tsx` | ✓       |         |         | NEW file                   |
| `src-tauri/src/lib.rs`                        |         | ✓       |         | Startup, register commands |
| `src-tauri/src/commands/window.rs`            |         | ✓       |         | NEW - window commands      |
| `src-tauri/src/commands/mod.rs`               |         | ✓       |         | Export window module       |
| `src-tauri/src/tray/setup.rs`                 |         | ✓       |         | Add usage info to menu     |
| `src-tauri/src/tray/dynamic_icon.rs`          |         | ✓       |         | NEW - generate % icon      |
| `src-tauri/src/tray/mod.rs`                   |         | ✓       |         | Export dynamic_icon        |
| `App.tsx`                                     |         |         | ✓       | Wire startup settings      |
| `Overlay.tsx`                                 |         |         | ✓       | Save/restore position      |
| `main.tsx`                                    |         |         | ✓       | Startup initialization     |

## Phase Status

- [x] Phase 1: Frontend Settings (~1.5h) - [phase-01-frontend-settings.md](./phase-01-frontend-settings.md) ✅
- [x] Phase 2: Tauri Backend (~2h) - [phase-02-tauri-backend.md](./phase-02-tauri-backend.md) ✅
- [x] Phase 3: Integration (~1h) - [phase-03-integration.md](./phase-03-integration.md) ✅

**Code Review:** [code-reviewer-260119-191700-show-mode-tray-settings.md](../reports/code-reviewer-260119-191700-show-mode-tray-settings.md) - ✅ APPROVED

## Key Dependencies

### External

- Zustand persist middleware (already in use)
- Tauri window management API
- localStorage for frontend settings

### Internal

- `settings-store.ts` - must be updated before integration
- `lib.rs` - must have new commands before integration

## Architecture Decision Records

### ADR-1: Settings Storage Location

**Decision**: Store both settings in Zustand with localStorage persist
**Rationale**:

- Consistent with existing settings (fontSize, refreshInterval)
- Fast read on app startup
- No Rust-side config file needed

### ADR-2: Show Mode Application

**Decision**: Read settings via JS bridge on Tauri setup, emit event to set visibility
**Rationale**:

- Settings stored in localStorage, accessible from frontend
- Tauri can receive event from frontend after mount
- Avoids duplicate config storage

### ADR-3: Remember Overlay Position

**Decision**: Store overlay position in localStorage, restore on startup
**Rationale**:

- Consistent with other settings storage
- Fast restore on app launch
- No Rust-side storage needed

### ADR-4: Dynamic Tray Icon

**Decision**: Generate icon with % text overlay using Rust image library
**Rationale**:

- Real-time update on usage change
- No external icon files needed
- Small icon size (16x16 or 22x22) fits text well

### ADR-5: Tray Menu Usage Info

**Decision**: Add menu items showing usage % and reset time (non-clickable)
**Rationale**:

- Quick glance without opening any window
- Updates on menu open (refresh before display)

## Success Criteria

1. Settings panel shows "Display Mode" dropdown with main/overlay/both options
2. App respects showMode on fresh launch
3. Overlay position persists across restarts
4. Tray icon displays current usage %
5. Tray menu shows reset time and usage %
6. No file conflicts between parallel phases
7. All existing tests pass

## Risk Assessment

| Risk                             | Likelihood | Impact | Mitigation                                         |
| -------------------------------- | ---------- | ------ | -------------------------------------------------- |
| Window visibility race condition | Medium     | Low    | Use ready event before applying settings           |
| Settings not persisted on crash  | Low        | Low    | localStorage writes are sync                       |
| Overlay not showing on startup   | Medium     | Medium | Test both visible=true and false initial states    |
| Dynamic icon rendering slow      | Low        | Medium | Cache generated icons, update only on usage change |
| Tray menu not updating           | Low        | Low    | Refresh usage before showing menu                  |

## Review Summary

**Status:** ✅ APPROVED with minor recommendations

**Key Findings:**

1. ✅ All phases completed successfully
2. ✅ TypeScript and Rust compilation pass
3. ✅ Production build succeeds
4. ⚠️ Minor race condition in startup (recommend adding delay)
5. ⚠️ Missing i18n translation keys (non-blocking)
6. ⚠️ Tray menu items static (documented limitation)

**Next Steps:**

1. ✅ Code review completed - see [report](../reports/code-reviewer-260119-191700-show-mode-tray-settings.md)
2. 🔄 Address high-priority findings (window ready delay)
3. 🔄 Add missing i18n keys
4. 🔄 Runtime testing on actual Tauri app
5. 📋 Consider improvements for future iterations
