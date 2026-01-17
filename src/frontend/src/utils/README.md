# Frontend Integration Utilities

Integration utilities for claudeminder frontend to handle tray updates, notifications, rate limiting, offline detection, and token refresh.

## Files

- **tray.ts** - System tray update utilities
- **notifications.ts** - Notification helpers with throttling
- **rate-limit.ts** - Rate limit handler with exponential backoff
- **offline-detector.ts** - Offline mode detection and retry logic
- **token-refresh.ts** - Token expiration handling and login flow

## Usage Examples

### Tray Updates

```typescript
import { updateTray, animateTray } from "./utils";

// Update tray with usage info
await updateTray(75.5, "2026-01-17T18:00:00Z", 150, 200);

// Animate tray icon
await animateTray(1500);
```

### Notifications

```typescript
import {
  notifyUsageWarning,
  notifyResetSoon,
  notifyTokenExpired,
  handleSnooze,
} from "./utils";

// Send usage warning (auto-triggered at 75% and 90%)
await notifyUsageWarning(90.5);

// Notify before reset
await notifyResetSoon(30); // 30 minutes

// Notify token expired
await notifyTokenExpired();

// Snooze notifications
await handleSnooze(60); // Snooze for 60 minutes
```

### Rate Limiting

```typescript
import { RateLimitHandler, executeWithBackoff } from "./utils";

// Using default handler
const data = await executeWithBackoff(
  async () => await fetchUsageData(),
  (attempt, delay) => console.log(`Retry ${attempt} in ${delay}ms`),
);

// Custom handler
const handler = new RateLimitHandler(5, 2000); // 5 retries, 2s base delay
const result = await handler.executeWithBackoff(async () => {
  return await apiCall();
});
```

### Offline Detection

```typescript
import { OfflineDetector, retryWithBackoff, checkNetworkError } from "./utils";

// Check if error is network-related
try {
  await fetchData();
} catch (error) {
  const isOffline = await checkNetworkError(error);
  if (isOffline) {
    console.log("Offline mode activated");
  }
}

// Retry with exponential backoff
const data = await retryWithBackoff(
  async () => await fetchUsageData(),
  (attempt, delay) => console.log(`Network retry ${attempt} in ${delay}ms`),
);

// Custom detector
const detector = new OfflineDetector(3, 1000);
const result = await detector.retryWithBackoff(async () => {
  return await apiCall();
});
```

### Token Refresh

```typescript
import {
  handleTokenExpired,
  openClaudeLogin,
  isTokenExpiredError,
  handlePotentialTokenExpiration,
} from "./utils";

// Handle token expiration
try {
  await fetchUsageData();
} catch (error) {
  if (isTokenExpiredError(error)) {
    await handleTokenExpired(); // Sends notification
    await openClaudeLogin(); // Opens browser
  }
}

// Automatic handling
try {
  await fetchUsageData();
} catch (error) {
  const handled = await handlePotentialTokenExpiration(error);
  if (!handled) {
    throw error; // Re-throw if not token error
  }
}
```

## Events Emitted

- `tray-update` - Tray icon update with payload: `{ utilization, tooltip, color }`
- `tray-animate` - Tray animation with payload: `{ duration }`
- `offline-mode` - Offline status change with payload: `{ offline: boolean }`
- `snooze` - Snooze request with payload: `{ duration_minutes }`

## Constants

- `NOTIFICATION_THROTTLE_MS` - 60000ms (1 minute between notifications)
- `CLAUDE_LOGIN_URL` - https://claude.ai/login

## Error Handling

All functions include proper error handling with try-catch blocks and console logging. Network errors, rate limits, and token expiration are detected automatically.

## Dependencies

- `@tauri-apps/api/event` - Event emission
- `@tauri-apps/plugin-notification` - System notifications
- `@tauri-apps/plugin-shell` - Browser opening
