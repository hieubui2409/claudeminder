# Phase 3: Integration

## Context Links

- [Main Plan](./plan.md)
- [Phase 1: Frontend Settings](./phase-01-frontend-settings.md)
- [Phase 2: Tauri Backend](./phase-02-tauri-backend.md)
- [App.tsx](../../src/frontend/src/App.tsx)
- [Overlay.tsx](../../src/frontend/src/Overlay.tsx)
- [main.tsx](../../src/frontend/src/main.tsx)

## Parallelization Info

| Property       | Value              |
| -------------- | ------------------ |
| Can run with   | None               |
| Blocked by     | Phase 1, Phase 2   |
| Blocks         | None (final phase) |
| Estimated time | 1 hour             |

## Overview

- **Priority**: P2
- **Status**: completed
- **Description**: Wire frontend settings to Tauri backend, apply show mode on startup, save/restore overlay position, update tray with usage

## Key Insights

- Phase 1 provides: settings store with showMode
- Phase 2 provides: apply_show_mode, save/get_overlay_position, update_tray_with_usage commands
- Integration needed: call commands on app mount with stored settings
- Overlay needs to save position on drag end, restore on mount
- Tray icon needs update on every usage fetch

## Requirements

### Functional

- FR1: On app startup, apply showMode from settings to window visibility
- FR2: Overlay saves position on drag end to localStorage
- FR3: Overlay restores position on mount
- FR4: Tray icon updates with usage % on every refresh
- FR5: Settings changes take effect on next app launch (show mode)

### Non-Functional

- NFR1: No visible flash when applying show mode
- NFR2: Graceful degradation if Tauri command fails
- NFR3: Works in browser dev mode (skip Tauri calls)

## Architecture

### Startup Flow

```
App Launch
    │
    ▼
main.tsx renders
    │
    ▼
App.tsx mounts
    │
    ▼
useEffect (empty deps)
    │
    ├── Read showMode from localStorage
    │
    ├── if (isTauri()) invoke("apply_show_mode", { mode })
    │
    └── Continue normal rendering
```

### Overlay Position Flow

```
Overlay mounts
    │
    ├── Read position from localStorage
    │
    ├── if (isTauri()) invoke("save_overlay_position", { position })
    │
    └── On drag end → save to localStorage + invoke save_overlay_position
```

### Tray Update Flow

```
useUsage hook fetches data
    │
    ▼
On success
    │
    ├── Update UI state
    │
    └── if (isTauri()) invoke("update_tray_with_usage", { percentage, resetTime })
```

## Related Code Files

### To Modify

| File                                  | Changes                           |
| ------------------------------------- | --------------------------------- |
| `src/frontend/src/App.tsx`            | Add startup show mode application |
| `src/frontend/src/Overlay.tsx`        | Add position save/restore         |
| `src/frontend/src/main.tsx`           | (optional) early settings read    |
| `src/frontend/src/hooks/use-usage.ts` | Add tray update on usage fetch    |

## File Ownership

**CRITICAL**: This phase owns these files exclusively:

- `App.tsx`
- `Overlay.tsx`
- `main.tsx`
- `hooks/use-usage.ts` (tray update integration only)

**Dependencies from other phases**:

- `settings-store.ts` - import showMode (Phase 1)
- `apply_show_mode` command - invoke from Tauri (Phase 2)
- `save_overlay_position`, `get_overlay_position` commands (Phase 2)
- `update_tray_with_usage` command (Phase 2)

## Implementation Steps

### Step 1: Update App.tsx - Apply Show Mode on Startup

Add effect after existing useEffects:

```typescript
// Apply show mode on startup
useEffect(() => {
  if (!isTauri()) return;

  const applyShowMode = async () => {
    try {
      // Read directly from localStorage to get initial value
      const stored = localStorage.getItem("claudeminder-settings");
      if (stored) {
        const settings = JSON.parse(stored);
        const mode = settings.state?.showMode || "main";
        await invoke("apply_show_mode", { mode });
      }
    } catch (err) {
      console.error("Failed to apply show mode:", err);
    }
  };

  applyShowMode();
}, []); // Run once on mount
```

### Step 2: Update Overlay.tsx - Save/Restore Position

Add position management:

```typescript
import { invoke } from "@tauri-apps/api/core";

const POSITION_KEY = "claudeminder-overlay-position";

interface Position {
  x: number;
  y: number;
}

export default function Overlay() {
  // ... existing state ...

  // Restore position on mount
  useEffect(() => {
    if (!isTauri()) return;

    const restorePosition = async () => {
      try {
        // First try localStorage
        const stored = localStorage.getItem(POSITION_KEY);
        if (stored) {
          const position: Position = JSON.parse(stored);
          await invoke("save_overlay_position", { position });
        }
      } catch (err) {
        console.error("Failed to restore overlay position:", err);
      }
    };

    restorePosition();
  }, []);

  // Save position on drag end
  const handleDragEnd = async () => {
    if (!isTauri()) return;

    try {
      const position = await invoke<Position>("get_overlay_position");
      localStorage.setItem(POSITION_KEY, JSON.stringify(position));
    } catch (err) {
      console.error("Failed to save overlay position:", err);
    }
  };

  // ... rest of component ...

  return (
    <div
      className={styles.overlay}
      data-tauri-drag-region
      onMouseUp={handleDragEnd}  // Save position after drag
    >
      {/* ... content ... */}
    </div>
  );
}
```

### Step 3: Update useUsage Hook - Tray Update

Add tray update after successful fetch:

```typescript
import { invoke } from "@tauri-apps/api/core";

// In fetchUsage function, after successful response:
const fetchUsage = useCallback(async () => {
  try {
    // ... existing fetch logic ...

    if (data) {
      setUsage(data);

      // Update tray icon and tooltip
      if (isTauri() && data.five_hour) {
        const percentage = Math.round(data.five_hour.utilization);
        const resetTime = formatResetTime(new Date(data.five_hour.resets_at));
        try {
          await invoke("update_tray_with_usage", {
            percentage,
            resetTime,
          });
        } catch (err) {
          console.error("Failed to update tray:", err);
        }
      }
    }
  } catch (err) {
    // ... existing error handling ...
  }
}, []);

// Helper function
function formatResetTime(resetDate: Date): string {
  const now = new Date();
  const diff = resetDate.getTime() - now.getTime();
  const hours = Math.floor(diff / (1000 * 60 * 60));
  const minutes = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60));

  if (hours > 0) {
    return `${hours}h ${minutes}m`;
  }
  return `${minutes}m`;
}
```

### Step 4: (Optional) Early Show Mode in main.tsx

For faster show mode application before React renders:

```typescript
// Early show mode application (before React)
const applyEarlyShowMode = async () => {
  if (typeof window.__TAURI__ === "undefined") return;

  try {
    const stored = localStorage.getItem("claudeminder-settings");
    if (stored) {
      const settings = JSON.parse(stored);
      const mode = settings.state?.showMode || "main";

      const { invoke } = await import("@tauri-apps/api/core");
      await invoke("apply_show_mode", { mode });
    }
  } catch (err) {
    console.error("Early show mode failed:", err);
  }
};

// Apply before React mount
applyEarlyShowMode();

// ... rest of main.tsx
```

## Todo List

- [x] Add apply_show_mode effect to App.tsx
- [x] Add position save/restore to Overlay.tsx
- [x] Update useUsage hook with tray update
- [x] Add formatResetTime helper
- [x] Test show mode "main" - main visible, overlay hidden
- [x] Test show mode "overlay" - overlay visible, main hidden
- [x] Test show mode "both" - both visible
- [x] Test overlay position persistence
- [x] Test tray icon updates with usage %
- [x] Verify browser dev mode still works

## Success Criteria

1. Fresh app launch respects stored showMode setting
2. Changing showMode in settings affects next launch
3. Overlay position persists across restarts
4. Tray icon shows current usage % with color coding
5. Tray tooltip shows usage info
6. No console errors in browser dev mode
7. No visible flash when switching show modes
8. All existing functionality preserved

## Conflict Prevention

This phase is sequential - no parallel work. However:

**Verify Phase 1 completed**:

- `useSettingsStore` exports showMode
- Types are correct

**Verify Phase 2 completed**:

- `apply_show_mode` command registered
- `save_overlay_position`, `get_overlay_position` commands work
- `update_tray_with_usage` command works

## Risk Assessment

| Risk                                | Likelihood | Impact | Mitigation                        |
| ----------------------------------- | ---------- | ------ | --------------------------------- |
| Zustand not hydrated on mount       | Medium     | Low    | Read localStorage directly        |
| Race between React render and Tauri | Medium     | Low    | Use async/await, handle errors    |
| Browser mode crashes                | Low        | Medium | isTauri() guards                  |
| Position not saved on quick close   | Low        | Low    | Save on mouseup, not window close |

## Security Considerations

- No new security concerns
- Only reading from localStorage (user's own data)
- Only invoking existing Tauri commands

## Testing Scenarios

### Scenario 1: Default Settings (First Launch)

1. Clear localStorage
2. Launch app
3. Expected: Main window visible, overlay hidden

### Scenario 2: Show Mode = "overlay"

1. Set showMode to "overlay" in settings
2. Restart app
3. Expected: Overlay visible, main hidden

### Scenario 3: Show Mode = "both"

1. Set showMode to "both" in settings
2. Restart app
3. Expected: Both windows visible

### Scenario 4: Overlay Position Persistence

1. Drag overlay to new position
2. Restart app
3. Expected: Overlay at saved position

### Scenario 5: Tray Icon Update

1. Wait for usage fetch
2. Check tray icon
3. Expected: Shows usage % with correct color

### Scenario 6: Browser Dev Mode

1. Run `bun dev`
2. Open in browser
3. Expected: No Tauri errors, app works without window commands

## Next Steps

After completion:

1. Run full integration tests
2. Test on Linux (primary target)
3. Update documentation if needed
4. Mark plan as completed
5. Create PR for review
