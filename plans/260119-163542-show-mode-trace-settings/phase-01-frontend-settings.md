# Phase 1: Frontend Settings

## Context Links

- [Main Plan](./plan.md)
- [Settings Store](../../src/frontend/src/stores/settings-store.ts)
- [Settings Types](../../src/frontend/src/types/settings.ts)
- [Settings Panel](../../src/frontend/src/components/settings/SettingsPanel.tsx)

## Parallelization Info

| Property       | Value                   |
| -------------- | ----------------------- |
| Can run with   | Phase 2 (Tauri Backend) |
| Blocked by     | None                    |
| Blocks         | Phase 3 (Integration)   |
| Estimated time | 1.5 hours               |

## Overview

- **Priority**: P2
- **Status**: pending
- **Description**: Add showMode setting to frontend, create UI component

## Key Insights

- Existing settings store uses Zustand + persist middleware to localStorage
- Settings panel organized by sections: General, Reminders, Appearance, Language
- Show Mode affects window visibility on startup (applied once, requires restart)
- Trace setting removed (always enabled per validation)

## Requirements

### Functional

- FR1: Add ShowMode type with values "main" | "overlay" | "both"
- FR2: Add showMode setting with default "main"
- FR3: Display mode select component in General section

### Non-Functional

- NFR1: Settings persist across app restarts
- NFR2: Components follow existing design patterns
- NFR3: Support i18n translations

## Architecture

### Data Flow

```
┌─────────────────┐
│ settings-store  │◄─── localStorage (persist)
│ - showMode      │
└────────┬────────┘
         │
         ▼
┌──────────────────┐
│ DisplayModeSelect│
└──────────────────┘
```

### Component Structure

```
 SettingsPanel
├── General Section
│   ├── RefreshIntervalSlider (existing)
│   └── DisplayModeSelect (NEW)
├── Reminders Section
├── Appearance Section
└── Language Section
```

## Related Code Files

### To Modify

| File                                                     | Changes                         |
| -------------------------------------------------------- | ------------------------------- |
| `src/frontend/src/stores/settings-store.ts`              | Add showMode, setShowMode       |
| `src/frontend/src/types/settings.ts`                     | Add ShowMode type               |
| `src/frontend/src/components/settings/SettingsPanel.tsx` | Import and render new component |

### To Create

| File                                                           | Purpose                |
| -------------------------------------------------------------- | ---------------------- |
| `src/frontend/src/components/settings/display-mode-select.tsx` | Dropdown for show mode |

## File Ownership

**CRITICAL**: This phase ONLY modifies frontend files. Do NOT touch:

- Any files in `src-tauri/`
- `App.tsx`, `Overlay.tsx`, `main.tsx` (reserved for Phase 3)

## Implementation Steps

### Step 1: Add Types (types/settings.ts)

Add ShowMode type:

```typescript
export type ShowMode = "main" | "overlay" | "both";
```

### Step 2: Update Settings Store (stores/settings-store.ts)

Add to SettingsStore interface:

```typescript
showMode: ShowMode;
setShowMode: (mode: ShowMode) => void;
```

Add to store implementation:

```typescript
showMode: "main",
setShowMode: (mode) => set({ showMode: mode }),
```

### Step 3: Create DisplayModeSelect Component

Location: `src/frontend/src/components/settings/display-mode-select.tsx`

```typescript
import { useTranslation } from "react-i18next";
import { useSettingsStore } from "../../stores/settings-store";
import type { ShowMode } from "../../types/settings";
import styles from "./SettingsPanel.module.css";

export function DisplayModeSelect() {
  const { t } = useTranslation();
  const { showMode, setShowMode } = useSettingsStore();

  const options: { value: ShowMode; label: string }[] = [
    { value: "main", label: t("settings.showMode.main", "Main window only") },
    { value: "overlay", label: t("settings.showMode.overlay", "Overlay only") },
    { value: "both", label: t("settings.showMode.both", "Both windows") },
  ];

  return (
    <div className={styles.settingItem}>
      <label className={styles.settingLabel}>
        {t("settings.showMode.label", "Display on startup")}
      </label>
      <select
        className={styles.select}
        value={showMode}
        onChange={(e) => setShowMode(e.target.value as ShowMode)}
      >
        {options.map((opt) => (
          <option key={opt.value} value={opt.value}>
            {opt.label}
          </option>
        ))}
      </select>
      <p className={styles.settingDescription}>
        {t("settings.showMode.description", "Choose which windows appear when app starts (requires restart)")}
      </p>
    </div>
  );
}
```

### Step 4: Update SettingsPanel Component

Add import at top:

```typescript
import { DisplayModeSelect } from "./display-mode-select";
```

Add after RefreshIntervalSlider in General section:

```tsx
<DisplayModeSelect />
```

## Todo List

- [ ] Add ShowMode type to types/settings.ts
- [ ] Update settings-store.ts with showMode and setter
- [ ] Create display-mode-select.tsx component
- [ ] Update SettingsPanel.tsx to include new component
- [ ] Add CSS styles for select if needed
- [ ] Add i18n translation keys

## Success Criteria

1. Settings store exposes showMode with correct default ("main")
2. DisplayModeSelect renders dropdown with 3 options
3. Settings persist after page reload (check localStorage)
4. No TypeScript errors
5. Existing tests pass

## Conflict Prevention

**DO NOT** modify these files (owned by other phases):

- `src-tauri/*` (Phase 2)
- `App.tsx` (Phase 3)
- `Overlay.tsx` (Phase 3)
- `main.tsx` (Phase 3)

**Coordinate** if CSS module changes affect:

- SettingsPanel.module.css (add styles, don't remove existing)

## Risk Assessment

| Risk                                       | Likelihood | Impact | Mitigation                            |
| ------------------------------------------ | ---------- | ------ | ------------------------------------- |
| CSS conflicts with existing styles         | Low        | Low    | Use scoped module CSS                 |
| Store migration breaking existing settings | Low        | High   | Persist middleware handles new fields |

## Security Considerations

- Settings stored in localStorage (client-side only)
- No sensitive data in showMode
- No API calls for settings changes

## Next Steps

After completion:

1. Notify Phase 3 that frontend settings are ready
2. Provide test instructions for settings verification
3. Document any CSS additions for design review
