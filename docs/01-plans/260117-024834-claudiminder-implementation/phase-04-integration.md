---
title: "Phase 4: Integration"
status: pending
priority: P1
effort: 6h
---

# Phase 4: Sidecar Integration, Tray, Notifications

## Context Links

- [Tauri v2 Research](../reports/researcher-260117-024702-tauri-v2-features.md)
- [UI Themes Research](../reports/researcher-260117-024115-ui-themes-design.md)
- Phase 1: Backend sidecar.py
- Phase 2: Rust sidecar module

## Overview

Complete integration between Python backend sidecar and Tauri frontend. Implement dynamic tray icon updates with configurable styles, desktop notifications with reminder schedules, snooze functionality, offline mode detection, rate limit handling, token refresh flow, and window management. Build Python backend using Nuitka (NOT PyInstaller).

## Key Insights (from research)

- Sidecar binary needs target-triple naming (e.g., `claudeminder-backend-x86_64-unknown-linux-gnu`)
- Tray tooltip updates via frontend event → Rust listener
- Notification plugin requires permission check at startup
- Dynamic SVG icons show percentage as circular progress
- Nuitka produces smaller, faster binaries than PyInstaller
- Certificate pinning prevents MITM attacks
- Notification throttling prevents spam (max 1/min)
- Snooze actions need notification buttons
- Offline mode requires special UI state
- Rate limiting needs exponential backoff strategy

## Requirements

### Functional

- Sidecar executes Nuitka-compiled Python backend and returns JSON
- Tray icon shows configurable style (number + progress + color)
- Tray tooltip shows full details (usage %, reset time, requests)
- Tray icon animation (pulse) on notification
- Desktop notifications at configured reminder times
- Notification throttling (max 1/min)
- Snooze buttons (5/15/30 min) in notifications
- Token expired notification + button to open login
- Offline mode detection and special UI state
- Rate limit handling with exponential backoff
- HTTP proxy support via environment variable
- Certificate pinning for API requests
- Window hide-to-tray on close button

### Non-Functional

- Sidecar response < 2s
- Icon updates on usage change only
- Notification throttling (max 1/minute)
- Nuitka binary < 30MB

## Architecture

```
Integration Flow:
┌─────────────┐     invoke()     ┌──────────────┐   sidecar()   ┌────────────────┐
│   React UI  │ ───────────────► │ Rust Command │ ────────────► │ Python Backend │
│             │ ◄─────────────── │              │ ◄──────────── │  (Nuitka)      │
└─────────────┘  UsageResponse   └──────────────┘     JSON      └────────────────┘
       │                                                                  │
       │  emit("usage-updated")                             HTTPS + cert pinning
       ▼                                                     + HTTP_PROXY support
┌─────────────┐                                                          │
│  Tray Icon  │  ← Updates tooltip + icon + animation                    ▼
└─────────────┘                                                  ┌────────────────┐
       │                                                         │ Anthropic API  │
       │  emit("notification")                                  └────────────────┘
       ▼
┌─────────────┐
│ Notification│  ← Throttled (1/min) + Snooze buttons
└─────────────┘

Rate Limit Strategy:
1. Detect 429 response
2. Exponential backoff (1s → 2s → 4s → 8s)
3. Show warning notification
4. Retry or fail gracefully

Offline Detection:
1. Network error → Set offline mode
2. Show special UI state
3. Retry with exponential backoff
4. Resume on reconnection

Token Expired Flow:
1. Detect 401 response or missing token
2. Show notification: "Token expired. Click to login."
3. Button opens Claude login page
4. Wait for token in ~/.claude/.credentials.json
5. Auto-retry when token available
```

## Related Code Files

### Create

- `scripts/build-sidecar-nuitka.sh` - Nuitka build script for Python binary
- `src/frontend/src-tauri/src/events.rs` - Event definitions
- `src/frontend/src-tauri/src/http_client.rs` - HTTP client with cert pinning + proxy
- `src/frontend/src/utils/tray.ts` - Tray update utilities (icon generation)
- `src/frontend/src/utils/notifications.ts` - Notification helpers (throttling + snooze)
- `src/frontend/src/utils/rate-limit.ts` - Rate limit handler with backoff
- `src/frontend/src/utils/offline-detector.ts` - Offline mode detection
- `src/frontend/src/utils/token-refresh.ts` - Token expired handler
- `src/frontend/src-tauri/icons/tray/` - Dynamic tray icons (SVG-based)

### Modify

- `src/backend/sidecar.py` - Add proxy support + rate limit detection
- `src/backend/api/client.py` - Add cert pinning + proxy config
- `src/frontend/src-tauri/src/main.rs` - Add event listeners + snooze handlers
- `src/frontend/src-tauri/src/tray/setup.rs` - Dynamic updates + animation
- `src/frontend/src/hooks/use-usage.ts` - Emit tray events + offline detection
- `src/frontend/src/App.tsx` - Notification scheduling + snooze logic
- `src/frontend/src/components/dashboard/dashboard-widget.tsx` - Offline UI state

## Implementation Steps

### Step 1: Create Nuitka Build Script

**scripts/build-sidecar-nuitka.sh:**

```bash
#!/bin/bash
set -e

# Detect target triple
case "$(uname -s)-$(uname -m)" in
    Linux-x86_64) TARGET="x86_64-unknown-linux-gnu" ;;
    Linux-aarch64) TARGET="aarch64-unknown-linux-gnu" ;;
    Darwin-x86_64) TARGET="x86_64-apple-darwin" ;;
    Darwin-arm64) TARGET="aarch64-apple-darwin" ;;
    MINGW*|MSYS*) TARGET="x86_64-pc-windows-msvc"; EXT=".exe" ;;
    *) echo "Unknown platform"; exit 1 ;;
esac

echo "Building sidecar for $TARGET with Nuitka..."

# Build Python with Nuitka
cd src/backend
uv run nuitka --standalone \
    --onefile \
    --output-filename="claudeminder-backend-$TARGET$EXT" \
    --enable-plugin=anti-bloat \
    --assume-yes-for-downloads \
    --remove-output \
    sidecar.py

# Copy to Tauri binaries
mkdir -p ../frontend/src-tauri/binaries
cp claudeminder-backend-$TARGET$EXT ../frontend/src-tauri/binaries/

echo "Sidecar built: binaries/claudeminder-backend-$TARGET$EXT"
echo "Size: $(du -h ../frontend/src-tauri/binaries/claudeminder-backend-$TARGET$EXT | cut -f1)"
```

### Step 2: Update API Client with Cert Pinning + Proxy

**src/backend/api/client.py:**

```python
"""HTTP client with certificate pinning and proxy support."""
from __future__ import annotations

import os
from typing import Any

import httpx
from loguru import logger
from tenacity import retry, stop_after_attempt, wait_exponential

# Anthropic API certificate fingerprints (SHA256)
CERT_FINGERPRINTS = [
    "sha256/AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA=",  # Primary cert
    "sha256/BBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBB=",  # Backup cert
]


class RateLimitError(Exception):
    """Raised when rate limit is exceeded."""

    pass


class TokenExpiredError(Exception):
    """Raised when OAuth token is expired."""

    pass


def get_http_client() -> httpx.AsyncClient:
    """Create HTTP client with cert pinning and proxy support."""
    proxies = {}
    if http_proxy := os.getenv("HTTP_PROXY") or os.getenv("http_proxy"):
        proxies["http://"] = http_proxy
    if https_proxy := os.getenv("HTTPS_PROXY") or os.getenv("https_proxy"):
        proxies["https://"] = https_proxy

    return httpx.AsyncClient(
        timeout=30.0,
        proxies=proxies if proxies else None,
        verify=True,  # Enable SSL verification
        # TODO: Implement certificate pinning with custom transport
    )


@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=1, max=8),
    reraise=True,
)
async def api_request(
    method: str,
    url: str,
    token: str,
    **kwargs: Any,
) -> dict[str, Any]:
    """Make API request with retry and error handling."""
    async with get_http_client() as client:
        headers = {"Authorization": f"Bearer {token}"}
        response = await client.request(method, url, headers=headers, **kwargs)

        if response.status_code == 401:
            raise TokenExpiredError("OAuth token expired")

        if response.status_code == 429:
            logger.warning("Rate limit exceeded")
            raise RateLimitError("Rate limit exceeded")

        response.raise_for_status()
        return response.json()
```

### Step 3: Update sidecar.py with Enhanced Error Handling

**src/backend/sidecar.py:**

```python
"""Sidecar entry point for Tauri integration."""
from __future__ import annotations

import asyncio
import json
import sys

from .api.client import RateLimitError, TokenExpiredError
from .api.usage import clear_usage_cache, get_usage_async
from .utils.credentials import is_token_available


async def handle_action(action: str) -> dict:
    """Handle sidecar action and return JSON response."""
    match action:
        case "get_usage":
            if not is_token_available():
                return {
                    "error": "No OAuth token",
                    "token_expired": True,
                }

            try:
                usage = await get_usage_async()
                if usage:
                    return usage.model_dump()
                return {"error": "Failed to fetch usage"}
            except TokenExpiredError:
                return {
                    "error": "OAuth token expired",
                    "token_expired": True,
                }
            except RateLimitError:
                return {
                    "error": "Rate limit exceeded",
                    "rate_limited": True,
                }
            except Exception as e:
                # Network error → offline mode
                if "connection" in str(e).lower() or "network" in str(e).lower():
                    return {
                        "error": "Network error",
                        "offline": True,
                    }
                return {"error": str(e)}

        case "refresh_usage":
            clear_usage_cache()
            return await handle_action("get_usage")

        case "check_token":
            return {"available": is_token_available()}

        case _:
            return {"error": f"Unknown action: {action}"}


async def main() -> None:
    action = sys.argv[1] if len(sys.argv) > 1 else "get_usage"
    result = await handle_action(action)
    print(json.dumps(result))


if __name__ == "__main__":
    asyncio.run(main())
```

### Step 4: Create Event Definitions (Rust)

**src/frontend/src-tauri/src/events.rs:**

```rust
use serde::{Deserialize, Serialize};

pub const EVENT_USAGE_UPDATED: &str = "usage-updated";
pub const EVENT_TRAY_UPDATE: &str = "tray-update";
pub const EVENT_TRAY_ANIMATE: &str = "tray-animate";
pub const EVENT_SNOOZE: &str = "snooze";

#[derive(Clone, Serialize, Deserialize)]
pub struct UsageUpdatedPayload {
    pub utilization: f64,
    pub resets_at: String,
    pub requests_used: u32,
    pub requests_limit: u32,
}

#[derive(Clone, Serialize, Deserialize)]
pub struct TrayUpdatePayload {
    pub percentage: f64,
    pub tooltip: String,
    pub color: String, // "green", "yellow", "orange", "red"
}

#[derive(Clone, Serialize, Deserialize)]
pub struct TrayAnimatePayload {
    pub duration_ms: u32,
}

#[derive(Clone, Serialize, Deserialize)]
pub struct SnoozePayload {
    pub minutes: u32, // 5, 15, 30
}
```

### Step 5: Update main.rs with Event Listeners

**src/frontend/src-tauri/src/main.rs:**

```rust
#![cfg_attr(not(debug_assertions), windows_subsystem = "windows")]

mod commands;
mod events;
mod sidecar;
mod tray;

use events::{SnoozePayload, TrayAnimatePayload, TrayUpdatePayload};
use events::{EVENT_SNOOZE, EVENT_TRAY_ANIMATE, EVENT_TRAY_UPDATE};
use tauri::{Listener, Manager};

fn main() {
    tauri::Builder::default()
        .plugin(tauri_plugin_shell::init())
        .plugin(tauri_plugin_notification::init())
        .setup(|app| {
            let tray_id = tray::setup::setup_tray(app)?;

            // Listen for tray update events from frontend
            let app_handle = app.handle().clone();
            let tray_id_clone = tray_id.clone();
            app.listen(EVENT_TRAY_UPDATE, move |event| {
                if let Ok(payload) = serde_json::from_str::<TrayUpdatePayload>(event.payload()) {
                    if let Some(tray) = app_handle.tray_by_id(&tray_id_clone) {
                        let _ = tray.set_tooltip(Some(&payload.tooltip));
                        // TODO: Update icon based on percentage + color
                    }
                }
            });

            // Listen for tray animation events
            let app_handle = app.handle().clone();
            let tray_id_clone = tray_id.clone();
            app.listen(EVENT_TRAY_ANIMATE, move |event| {
                if let Ok(payload) = serde_json::from_str::<TrayAnimatePayload>(event.payload()) {
                    if let Some(_tray) = app_handle.tray_by_id(&tray_id_clone) {
                        // TODO: Implement pulse animation
                        // For now, just log
                        println!("Tray pulse animation: {}ms", payload.duration_ms);
                    }
                }
            });

            // Listen for snooze events
            let app_handle = app.handle().clone();
            app.listen(EVENT_SNOOZE, move |event| {
                if let Ok(payload) = serde_json::from_str::<SnoozePayload>(event.payload()) {
                    println!("Snooze for {} minutes", payload.minutes);
                    // Emit to frontend to handle snooze logic
                    let _ = app_handle.emit("snooze-activated", payload);
                }
            });

            // Intercept window close to hide instead
            let main_window = app.get_webview_window("main").unwrap();
            main_window.on_window_event(move |event| {
                if let tauri::WindowEvent::CloseRequested { api, .. } = event {
                    api.prevent_close();
                    if let Err(e) = event.window().hide() {
                        eprintln!("Failed to hide window: {}", e);
                    }
                }
            });

            // Request notification permission
            #[cfg(desktop)]
            {
                let handle = app.handle().clone();
                tauri::async_runtime::spawn(async move {
                    let _ = tauri_plugin_notification::NotificationExt::notification(&handle)
                        .request_permission()
                        .await;
                });
            }

            Ok(())
        })
        .invoke_handler(tauri::generate_handler![
            commands::usage::get_usage,
            commands::usage::refresh_usage,
        ])
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
```

### Step 6: Update Tray Setup to Return ID

**src/frontend/src-tauri/src/tray/setup.rs:**

```rust
use tauri::{
    menu::{Menu, MenuItem},
    tray::{MouseButton, MouseButtonState, TrayIconBuilder, TrayIconEvent, TrayIconId},
    App, Manager,
};

pub fn setup_tray(app: &App) -> Result<TrayIconId, Box<dyn std::error::Error>> {
    let quit = MenuItem::with_id(app, "quit", "Quit", true, None::<&str>)?;
    let show = MenuItem::with_id(app, "show", "Show", true, None::<&str>)?;
    let menu = Menu::with_items(app, &[&show, &quit])?;

    let tray = TrayIconBuilder::with_id("main-tray")
        .icon(app.default_window_icon().unwrap().clone())
        .menu(&menu)
        .tooltip("claudeminder: Loading...")
        .on_menu_event(|app, event| match event.id().as_ref() {
            "quit" => app.exit(0),
            "show" => {
                if let Some(window) = app.get_webview_window("main") {
                    let _ = window.show();
                    let _ = window.set_focus();
                }
            }
            _ => {}
        })
        .on_tray_icon_event(|tray, event| {
            if let TrayIconEvent::Click {
                button: MouseButton::Left,
                button_state: MouseButtonState::Up,
                ..
            } = event
            {
                if let Some(window) = tray.app_handle().get_webview_window("main") {
                    let _ = window.unminimize();
                    let _ = window.show();
                    let _ = window.set_focus();
                }
            }
        })
        .build(app)?;

    Ok(tray.id().clone())
}
```

### Step 7: Create Tray Update Utility (TypeScript)

**src/frontend/src/utils/tray.ts:**

```typescript
import { emit } from "@tauri-apps/api/event";

export interface TrayUpdatePayload {
  percentage: number;
  tooltip: string;
  color: "green" | "yellow" | "orange" | "red";
}

export async function updateTray(
  utilization: number,
  resetsAt: string,
  requestsUsed: number,
  requestsLimit: number,
): Promise<void> {
  const percentage = utilization * 100;

  // Calculate time remaining
  const resetTime = new Date(resetsAt).getTime();
  const now = Date.now();
  const remainingMs = Math.max(0, resetTime - now);
  const remainingMins = Math.floor(remainingMs / 60000);

  // Determine color based on usage
  let color: "green" | "yellow" | "orange" | "red";
  if (percentage < 50) color = "green";
  else if (percentage < 75) color = "yellow";
  else if (percentage < 90) color = "orange";
  else color = "red";

  // Build tooltip with full details
  let timeStr: string;
  if (remainingMins >= 60) {
    const hours = Math.floor(remainingMins / 60);
    const mins = remainingMins % 60;
    timeStr = `${hours}h ${mins}m`;
  } else if (remainingMins > 0) {
    timeStr = `${remainingMins}m`;
  } else {
    timeStr = "now!";
  }

  const tooltip = `claudeminder: ${percentage.toFixed(1)}% | ${requestsUsed}/${requestsLimit} requests | Reset in ${timeStr}`;

  await emit("tray-update", { percentage, tooltip, color });
}

export async function animateTray(durationMs = 500): Promise<void> {
  await emit("tray-animate", { duration_ms: durationMs });
}
```

### Step 8: Create Notification Utility with Throttling + Snooze

**src/frontend/src/utils/notifications.ts:**

```typescript
import {
  isPermissionGranted,
  requestPermission,
  sendNotification,
} from "@tauri-apps/plugin-notification";
import { emit } from "@tauri-apps/api/event";

let lastNotificationTime = 0;
const NOTIFICATION_THROTTLE_MS = 60000; // 1 minute

export async function ensureNotificationPermission(): Promise<boolean> {
  let granted = await isPermissionGranted();
  if (!granted) {
    const permission = await requestPermission();
    granted = permission === "granted";
  }
  return granted;
}

async function canNotify(): Promise<boolean> {
  const now = Date.now();
  if (now - lastNotificationTime < NOTIFICATION_THROTTLE_MS) {
    console.log("Notification throttled");
    return false;
  }

  const granted = await ensureNotificationPermission();
  if (!granted) {
    console.warn("Notification permission not granted");
    return false;
  }

  lastNotificationTime = now;
  return true;
}

export async function notifyReminder(
  title: string,
  body: string,
): Promise<void> {
  if (!(await canNotify())) return;

  sendNotification({
    title,
    body,
    // TODO: Add snooze action buttons (requires Tauri plugin enhancement)
  });

  // Emit tray animation
  emit("tray-animate", { duration_ms: 500 });
}

export async function notifyUsageWarning(percentage: number): Promise<void> {
  if (percentage >= 90) {
    await notifyReminder(
      "Claude Usage Critical",
      `You've used ${percentage.toFixed(0)}% of your quota!`,
    );
  } else if (percentage >= 75) {
    await notifyReminder(
      "Claude Usage Warning",
      `You've used ${percentage.toFixed(0)}% of your quota.`,
    );
  }
}

export async function notifyResetSoon(minutesRemaining: number): Promise<void> {
  await notifyReminder(
    "Claude Reset Soon",
    `Your token quota resets in ${minutesRemaining} minutes!`,
  );
}

export async function notifyTokenExpired(): Promise<void> {
  if (!(await canNotify())) return;

  sendNotification({
    title: "Claude Token Expired",
    body: "Click to login and refresh your token.",
    // TODO: Add action button to open login page
  });
}

export async function notifyOffline(): Promise<void> {
  if (!(await canNotify())) return;

  sendNotification({
    title: "Network Error",
    body: "Claudiminder is offline. Will retry automatically.",
  });
}

export async function notifyRateLimited(): Promise<void> {
  if (!(await canNotify())) return;

  sendNotification({
    title: "Rate Limited",
    body: "API rate limit exceeded. Retrying with backoff...",
  });
}

export function handleSnooze(minutes: number): void {
  console.log(`Snoozed for ${minutes} minutes`);
  emit("snooze", { minutes });
}
```

### Step 9: Create Rate Limit Handler

**src/frontend/src/utils/rate-limit.ts:**

```typescript
export class RateLimitHandler {
  private retryCount = 0;
  private maxRetries = 4;

  async executeWithBackoff<T>(
    fn: () => Promise<T>,
    onRetry?: (attempt: number, delayMs: number) => void,
  ): Promise<T> {
    for (let attempt = 0; attempt <= this.maxRetries; attempt++) {
      try {
        const result = await fn();
        this.retryCount = 0; // Reset on success
        return result;
      } catch (error: any) {
        if (error.rate_limited && attempt < this.maxRetries) {
          const delayMs = Math.pow(2, attempt) * 1000; // 1s, 2s, 4s, 8s
          console.warn(
            `Rate limited. Retry ${attempt + 1}/${this.maxRetries} after ${delayMs}ms`,
          );
          onRetry?.(attempt + 1, delayMs);

          await new Promise((resolve) => setTimeout(resolve, delayMs));
        } else {
          throw error;
        }
      }
    }

    throw new Error("Max retries exceeded");
  }
}
```

### Step 10: Create Offline Detector

**src/frontend/src/utils/offline-detector.ts:**

```typescript
import { emit } from "@tauri-apps/api/event";

export class OfflineDetector {
  private isOffline = false;
  private retryAttempts = 0;
  private maxRetries = 5;

  checkNetworkError(error: any): boolean {
    const isNetworkError =
      error.offline === true ||
      error.message?.includes("network") ||
      error.message?.includes("connection");

    if (isNetworkError && !this.isOffline) {
      this.isOffline = true;
      this.retryAttempts = 0;
      emit("offline-mode", { offline: true });
    }

    return isNetworkError;
  }

  async retryWithBackoff(
    fn: () => Promise<any>,
  ): Promise<{ success: boolean; data?: any }> {
    if (!this.isOffline) {
      return { success: true, data: await fn() };
    }

    while (this.retryAttempts < this.maxRetries) {
      const delayMs = Math.pow(2, this.retryAttempts) * 2000; // 2s, 4s, 8s, 16s, 32s
      console.log(
        `Offline retry ${this.retryAttempts + 1}/${this.maxRetries} after ${delayMs}ms`,
      );

      await new Promise((resolve) => setTimeout(resolve, delayMs));

      try {
        const data = await fn();
        this.isOffline = false;
        this.retryAttempts = 0;
        emit("offline-mode", { offline: false });
        return { success: true, data };
      } catch (error) {
        this.retryAttempts++;
        if (!this.checkNetworkError(error)) {
          // Not a network error, stop retrying
          throw error;
        }
      }
    }

    return { success: false };
  }
}
```

### Step 11: Create Token Refresh Handler

**src/frontend/src/utils/token-refresh.ts:**

```typescript
import { open } from "@tauri-apps/plugin-shell";
import { notifyTokenExpired } from "./notifications";

const CLAUDE_LOGIN_URL = "https://claude.ai/login";

export async function handleTokenExpired(): Promise<void> {
  await notifyTokenExpired();

  // TODO: Add notification action button to trigger this
  // For now, user can manually click notification
}

export async function openClaudeLogin(): Promise<void> {
  await open(CLAUDE_LOGIN_URL);
}

export function watchTokenFile(onTokenAvailable: () => void): () => void {
  // TODO: Implement file watcher for ~/.claude/.credentials.json
  // For now, poll every 5 seconds
  const interval = setInterval(async () => {
    try {
      // Check if token is available via sidecar
      const result = await invoke("check_token");
      if (result.available) {
        onTokenAvailable();
        clearInterval(interval);
      }
    } catch (error) {
      console.error("Token check failed:", error);
    }
  }, 5000);

  return () => clearInterval(interval);
}
```

### Step 12: Update use-usage Hook with All Features

**src/frontend/src/hooks/use-usage.ts:**

```typescript
import { invoke } from "@tauri-apps/api/core";
import { useCallback, useEffect, useRef, useState } from "react";
import type { UsageResponse } from "../types/usage";
import { updateTray } from "../utils/tray";
import {
  notifyUsageWarning,
  notifyOffline,
  notifyRateLimited,
} from "../utils/notifications";
import { RateLimitHandler } from "../utils/rate-limit";
import { OfflineDetector } from "../utils/offline-detector";
import { handleTokenExpired } from "../utils/token-refresh";

export function useUsage(pollInterval = 60000) {
  const [usage, setUsage] = useState<UsageResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [isOffline, setIsOffline] = useState(false);
  const [isRateLimited, setIsRateLimited] = useState(false);

  const lastPercentageRef = useRef<number | null>(null);
  const rateLimitHandler = useRef(new RateLimitHandler());
  const offlineDetector = useRef(new OfflineDetector());

  const fetchUsage = useCallback(async () => {
    try {
      setLoading(true);

      const result = await rateLimitHandler.current.executeWithBackoff(
        async () => {
          const res = await invoke<UsageResponse>("get_usage");

          // Check for errors
          if (res.token_expired) {
            await handleTokenExpired();
            throw new Error("Token expired");
          }

          if (res.rate_limited) {
            setIsRateLimited(true);
            await notifyRateLimited();
            throw new Error("Rate limited");
          }

          if (res.offline) {
            throw new Error("Network error");
          }

          return res;
        },
        (attempt, delayMs) => {
          console.log(`Rate limit retry ${attempt}, waiting ${delayMs}ms`);
        },
      );

      setIsRateLimited(false);
      setIsOffline(false);
      setUsage(result);
      setError(result.error || null);

      // Update tray and check notifications
      if (result.five_hour) {
        const { utilization, resets_at } = result.five_hour;
        const percentage = utilization * 100;

        // Update tray with full details
        await updateTray(
          utilization,
          resets_at,
          result.five_hour.input_tokens_used || 0,
          result.five_hour.input_tokens_limit || 0,
        );

        // Check for usage warnings (only on increase)
        if (
          lastPercentageRef.current !== null &&
          percentage > lastPercentageRef.current
        ) {
          await notifyUsageWarning(percentage);
        }
        lastPercentageRef.current = percentage;
      }
    } catch (e: any) {
      // Check if offline
      if (offlineDetector.current.checkNetworkError(e)) {
        setIsOffline(true);
        await notifyOffline();

        // Retry with exponential backoff
        const retry = await offlineDetector.current.retryWithBackoff(async () =>
          invoke<UsageResponse>("get_usage"),
        );

        if (retry.success) {
          setIsOffline(false);
          setUsage(retry.data);
        }
      } else {
        setError(String(e));
      }
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchUsage();
    const interval = setInterval(fetchUsage, pollInterval);
    return () => clearInterval(interval);
  }, [fetchUsage, pollInterval]);

  return {
    usage,
    loading,
    error,
    isOffline,
    isRateLimited,
    refresh: fetchUsage,
  };
}
```

### Step 13: Update Dashboard Widget with Offline State

**src/frontend/src/components/dashboard/dashboard-widget.tsx:**

```typescript
// ... existing imports
import { useUsage } from "../../hooks/use-usage";

export function DashboardWidget() {
  const { usage, loading, error, isOffline, isRateLimited, refresh } =
    useUsage();

  if (loading) {
    return <div className="dashboard-loading">Loading...</div>;
  }

  if (isOffline) {
    return (
      <div className="dashboard-offline">
        <h3>Offline Mode</h3>
        <p>Claudiminder is offline. Retrying automatically...</p>
        <button onClick={refresh}>Retry Now</button>
      </div>
    );
  }

  if (isRateLimited) {
    return (
      <div className="dashboard-rate-limited">
        <h3>Rate Limited</h3>
        <p>API rate limit exceeded. Retrying with backoff...</p>
      </div>
    );
  }

  if (error) {
    return <div className="dashboard-error">Error: {error}</div>;
  }

  // ... rest of existing component
}
```

### Step 14: Add Reminder Scheduler to App with Snooze

**src/frontend/src/App.tsx (updated):**

```typescript
import { useEffect, useRef, useState } from "react";
import { listen } from "@tauri-apps/api/event";
import { DashboardWidget } from "./components/dashboard/dashboard-widget";
import { ThemeSwitcher } from "./components/settings/theme-switcher";
import { useThemeStore } from "./stores/theme-store";
import { useUsage } from "./hooks/use-usage";
import {
  notifyResetSoon,
  ensureNotificationPermission,
} from "./utils/notifications";
// ... CSS imports

const REMINDER_MINUTES = [30, 15, 5]; // Minutes before reset to notify

function App() {
  const { theme } = useThemeStore();
  const { usage } = useUsage();
  const notifiedMinutesRef = useRef<Set<number>>(new Set());
  const [snoozeUntil, setSnoozeUntil] = useState<number | null>(null);

  // Apply theme
  useEffect(() => {
    const mediaQuery = window.matchMedia("(prefers-color-scheme: dark)");
    const updateTheme = () => {
      document.documentElement.className =
        theme === "system" ? (mediaQuery.matches ? "dark" : "light") : theme;
    };
    updateTheme();
    mediaQuery.addEventListener("change", updateTheme);
    return () => mediaQuery.removeEventListener("change", updateTheme);
  }, [theme]);

  // Request notification permission on mount
  useEffect(() => {
    ensureNotificationPermission();
  }, []);

  // Listen for snooze events
  useEffect(() => {
    const unlisten = listen("snooze-activated", (event: any) => {
      const { minutes } = event.payload;
      const snoozeUntilTime = Date.now() + minutes * 60000;
      setSnoozeUntil(snoozeUntilTime);
      console.log(`Snoozed until ${new Date(snoozeUntilTime).toLocaleString()}`);
    });

    return () => {
      unlisten.then((fn) => fn());
    };
  }, []);

  // Reminder scheduler
  useEffect(() => {
    if (!usage?.five_hour) return;

    const checkReminders = () => {
      // Skip if snoozed
      if (snoozeUntil && Date.now() < snoozeUntil) {
        return;
      }

      const resetTime = new Date(usage.five_hour!.resets_at).getTime();
      const now = Date.now();
      const remainingMins = Math.floor((resetTime - now) / 60000);

      for (const reminderMin of REMINDER_MINUTES) {
        if (
          remainingMins <= reminderMin &&
          remainingMins > reminderMin - 1 &&
          !notifiedMinutesRef.current.has(reminderMin)
        ) {
          notifyResetSoon(remainingMins);
          notifiedMinutesRef.current.add(reminderMin);
        }
      }

      // Reset notified set when quota resets
      if (remainingMins <= 0) {
        notifiedMinutesRef.current.clear();
        setSnoozeUntil(null);
      }
    };

    checkReminders();
    const interval = setInterval(checkReminders, 30000); // Check every 30s
    return () => clearInterval(interval);
  }, [usage, snoozeUntil]);

  return (
    <main className="app-container">
      <DashboardWidget />
      <ThemeSwitcher />
    </main>
  );
}

export default App;
```

### Step 15: Add Nuitka to Dependencies

**src/backend/pyproject.toml:**

```toml
[project]
# ... existing fields

[project.optional-dependencies]
dev = [
    "pytest>=8.0.0",
    "pytest-asyncio>=0.23.0",
    "nuitka>=2.0.0",  # Add Nuitka for production builds
]
```

## Todo List

- [ ] Install Nuitka: `uv add --dev nuitka`
- [ ] Create `scripts/build-sidecar-nuitka.sh` with target detection
- [ ] Update `src/backend/api/client.py` with cert pinning + proxy support
- [ ] Update `sidecar.py` with error handling (token expired, rate limit, offline)
- [ ] Create `events.rs` with all event definitions
- [ ] Update `main.rs` with event listeners (tray, animation, snooze)
- [ ] Update `tray/setup.rs` to return TrayIconId
- [ ] Create `src/utils/tray.ts` for tray updates (icon generation)
- [ ] Create `src/utils/notifications.ts` with throttling + snooze
- [ ] Create `src/utils/rate-limit.ts` with exponential backoff
- [ ] Create `src/utils/offline-detector.ts` for offline mode detection
- [ ] Create `src/utils/token-refresh.ts` for token expired handler
- [ ] Update `use-usage.ts` to emit tray events + handle errors
- [ ] Update `dashboard-widget.tsx` with offline/rate-limited UI states
- [ ] Update `App.tsx` with reminder scheduler + snooze logic
- [ ] Add window close → hide behavior
- [ ] Test Nuitka build on current platform
- [ ] Test tray tooltip updates with full details
- [ ] Test notifications at reminder times
- [ ] Test snooze functionality (5/15/30 min)
- [ ] Test offline mode detection and retry
- [ ] Test rate limit handling with backoff
- [ ] Test token expired notification + login flow
- [ ] Test HTTP proxy support (HTTP_PROXY env var)

## Success Criteria

- Nuitka sidecar builds successfully (< 30MB)
- Sidecar executes and returns JSON in < 2s
- Tray tooltip shows "claudeminder: XX.X% | XXX/XXXX requests | Reset in Xh Xm"
- Tray icon changes color based on usage (green/yellow/orange/red)
- Tray icon animates (pulse) on notification
- Desktop notification appears 30/15/5 min before reset
- Notification throttling works (max 1/min)
- Snooze buttons work (5/15/30 min)
- Token expired notification shows with login button
- Offline mode shows special UI state and auto-retries
- Rate limit handling works with exponential backoff
- HTTP proxy support works (HTTP_PROXY env var)
- Window hides to tray on close button
- Window restores on tray click

## Risk Assessment

| Risk                                   | Mitigation                                |
| -------------------------------------- | ----------------------------------------- |
| Nuitka build issues on different OS    | Test on each target platform              |
| Certificate pinning breaks on cert rot | Use multiple cert fingerprints + fallback |
| Notification permission denied         | Fallback to console log + UI indicator    |
| Tray tooltip truncated on Windows      | Limit to 64 chars                         |
| Snooze state lost on app restart       | Persist to localStorage                   |
| Offline retry causing battery drain    | Max 5 retries with exponential backoff    |
| Rate limit causing infinite loop       | Max 4 retries then fail gracefully        |

## Security Considerations

- Sidecar runs with user permissions only
- No sensitive data in tray tooltip (no tokens)
- Notifications contain no tokens/credentials
- Event payloads validated before processing
- Certificate pinning prevents MITM attacks
- HTTP proxy respects system environment variables
- Token expiry detected before making API calls
