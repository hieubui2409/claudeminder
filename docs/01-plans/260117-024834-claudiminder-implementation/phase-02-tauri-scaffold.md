---
title: "Phase 2: Tauri Scaffold"
status: pending
priority: P1
effort: 4h
---

# Phase 2: Tauri v2 + React Project Scaffold

## Context Links

- [Tauri v2 Research](../reports/researcher-260117-024702-tauri-v2-features.md)
- [Tauri Rules](../../02-general/rules/02-tauri.md)

## Overview

Scaffold Tauri v2 desktop app with React + TypeScript frontend using Bun package manager. Configure Python sidecar (Nuitka build), tray icon, notifications, single instance, global hotkey, macOS menu bar, Touch Bar, update checker, HTTPS cert pinning, and proxy support.

## Key Insights (from research)

- `create-tauri-app` supports Bun natively
- Sidecar configured via `bundle.externalBin` (use Nuitka instead of PyInstaller)
- Shell plugin required for sidecar execution
- Notification plugin needs permission request at startup
- Tray uses `TrayIconBuilder` with `on_tray_icon_event`
- Single instance via `tauri-plugin-single-instance`
- Global hotkey via `tauri-plugin-global-shortcut` (user customizable)
- macOS menu bar mode uses NSStatusBar API
- Touch Bar widgets via macOS-specific API
- HTTPS cert pinning implemented in Rust HTTP client
- HTTP_PROXY env var support for corporate networks
- Update checker via `tauri-plugin-updater` (notify only, no auto-update)

## Requirements

### Functional

- React 18 + TypeScript strict mode
- Bun as package manager
- System tray with dynamic tooltip (full menu: Show, Refresh, Settings, About, Quit)
- macOS menu bar mode (NSStatusBar)
- macOS Touch Bar widgets (usage percentage, reset time)
- Window hide-to-tray behavior (resizable window)
- Python sidecar integration (Nuitka build instead of PyInstaller)
- Single instance enforcement (Rust plugin)
- Global hotkey (user customizable via settings)
- Update checker (notify only, no auto-update)
- HTTPS cert pinning for Anthropic API
- HTTP_PROXY environment variable support

### Non-Functional

- Dev hot-reload for both React & Rust
- < 50MB bundle size
- Cross-platform build targets

## Architecture

```
src/frontend/
├── src/                    # React frontend
│   ├── components/         # UI components
│   ├── hooks/              # Custom React hooks
│   ├── stores/             # Zustand state
│   ├── styles/             # CSS/theme files
│   ├── types/              # TypeScript types
│   ├── utils/              # Utility functions
│   ├── App.tsx
│   └── main.tsx
├── src-tauri/              # Rust backend
│   ├── src/
│   │   ├── main.rs         # Entry point
│   │   ├── lib.rs          # Library exports
│   │   ├── commands/       # IPC commands
│   │   │   ├── mod.rs
│   │   │   └── usage.rs
│   │   ├── tray/           # System tray
│   │   │   ├── mod.rs
│   │   │   └── setup.rs
│   │   └── sidecar/        # Python sidecar
│   │       ├── mod.rs
│   │       └── backend.rs
│   ├── icons/              # App icons
│   ├── capabilities/       # Permission files
│   ├── Cargo.toml
│   └── tauri.conf.json
├── index.html
├── package.json
├── tsconfig.json
├── vite.config.ts
└── bun.lockb
```

## Related Code Files

### Create (Tauri scaffold generates most, then customize)

- `src/frontend/src-tauri/src/main.rs`
- `src/frontend/src-tauri/src/lib.rs`
- `src/frontend/src-tauri/src/commands/mod.rs`
- `src/frontend/src-tauri/src/commands/usage.rs`
- `src/frontend/src-tauri/src/commands/settings.rs`
- `src/frontend/src-tauri/src/tray/mod.rs`
- `src/frontend/src-tauri/src/tray/setup.rs`
- `src/frontend/src-tauri/src/sidecar/mod.rs`
- `src/frontend/src-tauri/src/sidecar/backend.rs`
- `src/frontend/src-tauri/src/http_client/mod.rs`
- `src/frontend/src-tauri/src/macos/mod.rs` (macOS only)
- `src/frontend/src-tauri/capabilities/default.json`
- `src/frontend/src-tauri/certs/anthropic.pem`
- `src/frontend/src/types/usage.ts`
- `src/frontend/src/hooks/use-usage.ts`
- `scripts/build-sidecar.sh` (Nuitka build)

### Modify (after scaffold)

- `src/frontend/src-tauri/tauri.conf.json`
- `src/frontend/src-tauri/Cargo.toml`
- `README.md` (add proxy support docs)

## Implementation Steps

### Step 1: Create Tauri Project

```bash
cd /home/hieubt/Documents/ai-hub/claudiminder/src
bun create tauri-app frontend --template react-ts
cd frontend
```

Select options:

- Package manager: bun
- Frontend: React
- TypeScript: Yes

### Step 2: Initialize Tauri

```bash
cd src/frontend
bun install
bun add @tauri-apps/plugin-notification @tauri-apps/plugin-shell @tauri-apps/plugin-single-instance @tauri-apps/plugin-global-shortcut @tauri-apps/plugin-updater zustand
```

### Step 3: Configure tauri.conf.json

```json
{
  "$schema": "../node_modules/@tauri-apps/cli/config.schema.json",
  "productName": "claudiminder",
  "identifier": "com.claudiminder.app",
  "build": {
    "beforeDevCommand": "bun run dev",
    "devUrl": "http://localhost:5173",
    "beforeBuildCommand": "bun run build",
    "frontendDist": "../dist"
  },
  "bundle": {
    "active": true,
    "targets": "all",
    "externalBin": ["binaries/claudiminder-backend"],
    "icon": [
      "icons/32x32.png",
      "icons/128x128.png",
      "icons/icon.icns",
      "icons/icon.ico"
    ]
  },
  "app": {
    "windows": [
      {
        "title": "claudiminder",
        "width": 400,
        "height": 300,
        "resizable": true,
        "fullscreen": false,
        "visible": true,
        "center": true
      }
    ],
    "trayIcon": {
      "iconPath": "icons/tray.png",
      "iconAsTemplate": true
    },
    "security": {
      "csp": null
    }
  }
}
```

### Step 4: Configure Cargo.toml

Add to `src/frontend/src-tauri/Cargo.toml`:

```toml
[dependencies]
tauri = { version = "2", features = ["tray-icon", "macos-private-api"] }
tauri-plugin-shell = "2"
tauri-plugin-notification = "2"
tauri-plugin-single-instance = "2"
tauri-plugin-global-shortcut = "2"
tauri-plugin-updater = "2"
serde = { version = "1", features = ["derive"] }
serde_json = "1"
tokio = { version = "1", features = ["full"] }
reqwest = { version = "0.11", features = ["rustls-tls", "json"] }
rustls = "0.21"
rustls-native-certs = "0.6"

[target.'cfg(target_os = "macos")'.dependencies]
cocoa = "0.25"
objc = "0.2"
```

### Step 5: Create main.rs

```rust
#![cfg_attr(not(debug_assertions), windows_subsystem = "windows")]

mod commands;
mod sidecar;
mod tray;
mod http_client;
#[cfg(target_os = "macos")]
mod macos;

use tauri::Manager;

fn main() {
    tauri::Builder::default()
        .plugin(tauri_plugin_shell::init())
        .plugin(tauri_plugin_notification::init())
        .plugin(tauri_plugin_single_instance::init(|app, _args, _cwd| {
            // Bring existing instance to front
            if let Some(window) = app.get_webview_window("main") {
                let _ = window.show();
                let _ = window.set_focus();
            }
        }))
        .plugin(tauri_plugin_global_shortcut::Builder::new().build())
        .plugin(tauri_plugin_updater::Builder::new().build())
        .setup(|app| {
            tray::setup::setup_tray(app)?;

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

            // macOS-specific setup
            #[cfg(target_os = "macos")]
            {
                macos::setup_menu_bar(app)?;
                macos::setup_touch_bar(app)?;
            }

            // Register default global hotkey (Cmd+Shift+C on macOS, Ctrl+Shift+C on others)
            #[cfg(target_os = "macos")]
            let default_hotkey = "Cmd+Shift+C";
            #[cfg(not(target_os = "macos"))]
            let default_hotkey = "Ctrl+Shift+C";

            app.handle()
                .plugin(tauri_plugin_global_shortcut::GlobalShortcutExt::global_shortcut())
                .on_shortcut(default_hotkey, move |app, _shortcut, _event| {
                    if let Some(window) = app.get_webview_window("main") {
                        let _ = window.show();
                        let _ = window.set_focus();
                    }
                });

            // Check for updates on startup (notify only)
            let app_handle = app.handle().clone();
            tauri::async_runtime::spawn(async move {
                if let Ok(update) = app_handle.updater().check().await {
                    if update.is_update_available() {
                        let _ = tauri_plugin_notification::NotificationExt::notification(&app_handle)
                            .title("Update Available")
                            .body(format!("Version {} is available", update.version))
                            .show();
                    }
                }
            });

            Ok(())
        })
        .invoke_handler(tauri::generate_handler![
            commands::usage::get_usage,
            commands::usage::refresh_usage,
            commands::settings::set_global_hotkey,
        ])
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
```

### Step 6: Create lib.rs

```rust
pub mod commands;
pub mod sidecar;
pub mod tray;
pub mod http_client;
#[cfg(target_os = "macos")]
pub mod macos;
```

### Step 7: Create Commands Module

**commands/mod.rs:**

```rust
pub mod usage;
pub mod settings;
```

**commands/usage.rs:**

```rust
use crate::sidecar::backend::call_backend;
use serde::{Deserialize, Serialize};
use tauri::AppHandle;

#[derive(Debug, Serialize, Deserialize)]
pub struct UsageResponse {
    pub five_hour: Option<FiveHourUsage>,
    pub error: Option<String>,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct FiveHourUsage {
    pub utilization: f64,
    pub resets_at: String,
}

#[tauri::command]
pub async fn get_usage(app: AppHandle) -> Result<UsageResponse, String> {
    let output = call_backend(&app, "get_usage").await?;
    serde_json::from_str(&output).map_err(|e| e.to_string())
}

#[tauri::command]
pub async fn refresh_usage(app: AppHandle) -> Result<UsageResponse, String> {
    let output = call_backend(&app, "refresh_usage").await?;
    serde_json::from_str(&output).map_err(|e| e.to_string())
}
```

### Step 8: Create Sidecar Module

**sidecar/mod.rs:**

```rust
pub mod backend;
```

**sidecar/backend.rs:**

```rust
use tauri::AppHandle;
use tauri_plugin_shell::ShellExt;

pub async fn call_backend(app: &AppHandle, action: &str) -> Result<String, String> {
    let output = app
        .shell()
        .sidecar("claudiminder-backend")
        .map_err(|e| e.to_string())?
        .arg(action)
        .output()
        .await
        .map_err(|e| e.to_string())?;

    if output.status.success() {
        Ok(String::from_utf8_lossy(&output.stdout).to_string())
    } else {
        Err(String::from_utf8_lossy(&output.stderr).to_string())
    }
}
```

### Step 9: Create Tray Module

**tray/mod.rs:**

```rust
pub mod setup;
```

**tray/setup.rs:**

```rust
use tauri::{
    menu::{Menu, MenuItem},
    tray::{MouseButton, MouseButtonState, TrayIconBuilder, TrayIconEvent},
    App, Manager,
};

pub fn setup_tray(app: &App) -> Result<(), Box<dyn std::error::Error>> {
    let show = MenuItem::with_id(app, "show", "Show", true, None::<&str>)?;
    let refresh = MenuItem::with_id(app, "refresh", "Refresh", true, None::<&str>)?;
    let settings = MenuItem::with_id(app, "settings", "Settings", true, None::<&str>)?;
    let about = MenuItem::with_id(app, "about", "About", true, None::<&str>)?;
    let quit = MenuItem::with_id(app, "quit", "Quit", true, None::<&str>)?;

    let menu = Menu::with_items(app, &[&show, &refresh, &settings, &about, &quit])?;

    TrayIconBuilder::new()
        .icon(app.default_window_icon().unwrap().clone())
        .menu(&menu)
        .tooltip("claudiminder: Loading...")
        .on_menu_event(|app, event| match event.id().as_ref() {
            "quit" => app.exit(0),
            "show" => {
                if let Some(window) = app.get_webview_window("main") {
                    let _ = window.show();
                    let _ = window.set_focus();
                }
            }
            "refresh" => {
                // Emit refresh event to frontend
                let _ = app.emit("refresh-usage", ());
            }
            "settings" => {
                if let Some(window) = app.get_webview_window("main") {
                    let _ = window.show();
                    let _ = window.set_focus();
                    let _ = app.emit("navigate-to-settings", ());
                }
            }
            "about" => {
                if let Some(window) = app.get_webview_window("main") {
                    let _ = window.show();
                    let _ = window.set_focus();
                    let _ = app.emit("navigate-to-about", ());
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

    Ok(())
}
```

### Step 10: Create HTTP Client with Cert Pinning

**http_client/mod.rs:**

```rust
use reqwest::{Client, ClientBuilder};
use rustls::{Certificate, ClientConfig, RootCertStore};
use std::sync::Arc;

const ANTHROPIC_CERT_PEM: &str = include_str!("../../certs/anthropic.pem");

pub fn create_client() -> Result<Client, Box<dyn std::error::Error>> {
    let mut root_store = RootCertStore::empty();

    // Add system certificates
    for cert in rustls_native_certs::load_native_certs()? {
        root_store.add(&Certificate(cert.0))?;
    }

    // Add pinned Anthropic certificate
    let anthropic_cert = pem::parse(ANTHROPIC_CERT_PEM)?;
    root_store.add(&Certificate(anthropic_cert.contents))?;

    let tls_config = ClientConfig::builder()
        .with_safe_defaults()
        .with_root_certificates(root_store)
        .with_no_client_auth();

    let client = ClientBuilder::new()
        .use_preconfigured_tls(tls_config)
        .build()?;

    Ok(client)
}
```

### Step 11: Create macOS-specific Module

**macos/mod.rs:**

```rust
#[cfg(target_os = "macos")]
use cocoa::appkit::{NSStatusBar, NSStatusItem};
#[cfg(target_os = "macos")]
use cocoa::base::{id, nil};
#[cfg(target_os = "macos")]
use objc::{msg_send, sel, sel_impl};
use tauri::App;

#[cfg(target_os = "macos")]
pub fn setup_menu_bar(app: &App) -> Result<(), Box<dyn std::error::Error>> {
    unsafe {
        let status_bar = NSStatusBar::systemStatusBar(nil);
        let status_item: id = msg_send![status_bar, statusItemWithLength: -1.0];

        // Set icon and title
        let button: id = msg_send![status_item, button];
        let title = NSString::alloc(nil).init_str("📊");
        let _: () = msg_send![button, setTitle: title];
    }
    Ok(())
}

#[cfg(target_os = "macos")]
pub fn setup_touch_bar(app: &App) -> Result<(), Box<dyn std::error::Error>> {
    // Touch Bar setup will be implemented with usage data integration
    Ok(())
}

#[cfg(not(target_os = "macos"))]
pub fn setup_menu_bar(_app: &App) -> Result<(), Box<dyn std::error::Error>> {
    Ok(())
}

#[cfg(not(target_os = "macos"))]
pub fn setup_touch_bar(_app: &App) -> Result<(), Box<dyn std::error::Error>> {
    Ok(())
}
```

### Step 12: Create Settings Commands

**commands/settings.rs:**

```rust
use tauri::{AppHandle, State};
use tauri_plugin_global_shortcut::GlobalShortcutExt;

#[tauri::command]
pub async fn set_global_hotkey(app: AppHandle, hotkey: String) -> Result<(), String> {
    // Unregister old hotkey
    let shortcuts = app.global_shortcut();
    shortcuts.unregister_all().map_err(|e| e.to_string())?;

    // Register new hotkey
    shortcuts
        .on_shortcut(&hotkey, move |app, _shortcut, _event| {
            if let Some(window) = app.get_webview_window("main") {
                let _ = window.show();
                let _ = window.set_focus();
            }
        })
        .map_err(|e| e.to_string())?;

    Ok(())
}
```

### Step 13: Create Capabilities

**capabilities/default.json:**

```json
{
  "$schema": "../gen/schemas/desktop-schema.json",
  "identifier": "default",
  "description": "Default capabilities for claudiminder",
  "windows": ["main"],
  "permissions": [
    "core:default",
    "shell:allow-execute",
    "shell:allow-spawn",
    "notification:default",
    "notification:allow-is-permission-granted",
    "notification:allow-request-permission",
    "notification:allow-notify",
    "global-shortcut:allow-register",
    "global-shortcut:allow-unregister",
    "global-shortcut:allow-is-registered",
    "updater:default",
    "updater:allow-check"
  ]
}
```

### Step 14: Create TypeScript Types

**src/types/usage.ts:**

```typescript
export interface FiveHourUsage {
  utilization: number;
  resets_at: string;
}

export interface UsageResponse {
  five_hour: FiveHourUsage | null;
  error?: string;
}
```

### Step 15: Create Usage Hook

**src/hooks/use-usage.ts:**

```typescript
import { invoke } from "@tauri-apps/api/core";
import { useCallback, useEffect, useState } from "react";
import type { UsageResponse } from "../types/usage";

export function useUsage(pollInterval = 60000) {
  const [usage, setUsage] = useState<UsageResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchUsage = useCallback(async () => {
    try {
      setLoading(true);
      const result = await invoke<UsageResponse>("get_usage");
      setUsage(result);
      setError(result.error || null);
    } catch (e) {
      setError(String(e));
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchUsage();
    const interval = setInterval(fetchUsage, pollInterval);
    return () => clearInterval(interval);
  }, [fetchUsage, pollInterval]);

  return { usage, loading, error, refresh: fetchUsage };
}
```

### Step 16: Prepare Sidecar Binary with Nuitka

Create build script for Python sidecar using Nuitka:

```bash
# scripts/build-sidecar.sh
#!/bin/bash
set -e

cd src/backend

# Install Nuitka if not available
uv pip install nuitka

# Build with Nuitka (faster startup, no Python runtime required)
uv run nuitka3 \
  --standalone \
  --onefile \
  --output-dir=dist \
  --output-filename=claudiminder-backend \
  --remove-output \
  --assume-yes-for-downloads \
  claudiminder/cli.py

# Copy to frontend binaries
mkdir -p ../frontend/src-tauri/binaries
cp dist/claudiminder-backend ../frontend/src-tauri/binaries/

# Make executable
chmod +x ../frontend/src-tauri/binaries/claudiminder-backend

echo "Sidecar binary built successfully with Nuitka"
```

### Step 17: Add Proxy Support Environment

Document HTTP_PROXY support in README:

````markdown
## Proxy Support

claudiminder respects the `HTTP_PROXY` and `HTTPS_PROXY` environment variables for corporate network access.

### Linux/macOS

```bash
export HTTPS_PROXY=http://proxy.company.com:8080
claudiminder
```
````

### Windows

```powershell
$env:HTTPS_PROXY="http://proxy.company.com:8080"
claudiminder
```

```

## Todo List

- [ ] Run `bun create tauri-app frontend --template react-ts`
- [ ] Install Tauri plugins (shell, notification, single-instance, global-shortcut, updater)
- [ ] Configure `tauri.conf.json` with sidecar, tray, and resizable window
- [ ] Add dependencies to `Cargo.toml` (plugins, rustls, reqwest, macOS libs)
- [ ] Create `main.rs` with all plugin initialization
- [ ] Implement single instance enforcement
- [ ] Implement global hotkey registration (default + customizable)
- [ ] Implement update checker (notify only)
- [ ] Create `commands/usage.rs` IPC commands
- [ ] Create `commands/settings.rs` for hotkey management
- [ ] Create `sidecar/backend.rs` for Python execution
- [ ] Create `tray/setup.rs` with full menu (Show, Refresh, Settings, About, Quit)
- [ ] Create `http_client/mod.rs` with cert pinning and proxy support
- [ ] Create `macos/mod.rs` for menu bar and Touch Bar (macOS only)
- [ ] Create `capabilities/default.json` with all permissions
- [ ] Create TypeScript types for usage response
- [ ] Create `use-usage.ts` React hook
- [ ] Create Nuitka build script for sidecar
- [ ] Download and pin Anthropic SSL certificate
- [ ] Document HTTP_PROXY environment variable support
- [ ] Test with `bun run tauri dev`
- [ ] Test single instance behavior
- [ ] Test global hotkey registration
- [ ] Test update checker notification
- [ ] Test on macOS (menu bar + Touch Bar)

## Success Criteria

- `bun run tauri dev` launches app window (resizable)
- System tray icon appears with full menu (Show, Refresh, Settings, About, Quit)
- Tray left-click shows window
- Tray right-click shows full menu
- Only one instance can run (second launch brings first to front)
- Global hotkey (Cmd/Ctrl+Shift+C) shows window
- Update checker notifies on startup if update available
- `invoke("get_usage")` returns data from sidecar (Nuitka build)
- `invoke("set_global_hotkey")` updates hotkey successfully
- macOS: Menu bar icon shows in status bar
- macOS: Touch Bar widgets display (basic setup)
- HTTP_PROXY environment variable respected by HTTP client
- HTTPS connections use cert pinning for Anthropic API

## Risk Assessment

| Risk                                  | Mitigation                                    |
| ------------------------------------- | --------------------------------------------- |
| Sidecar path resolution varies by OS  | Use Tauri's target-triple naming              |
| Nuitka build complexity               | Test on all platforms, fallback to PyInstaller|
| Notification permission denied        | Show in-app fallback notification             |
| Rust compile errors                   | Follow Tauri v2 docs exactly                  |
| macOS private API rejection           | Use documented NSStatusBar APIs only          |
| Global hotkey conflicts               | Allow user customization, validate input      |
| Certificate pinning breaks with renewal| Monitor Anthropic cert updates, auto-update  |
| Proxy authentication                  | Document manual proxy auth configuration      |
| Touch Bar hardware unavailable        | Graceful fallback on non-Touch Bar Macs       |

## Security Considerations

- Minimal capabilities: shell, notification, global-shortcut, updater
- No file system access granted
- Sidecar runs in sandboxed context
- HTTPS cert pinning for Anthropic API prevents MITM attacks
- Proxy support respects system environment variables
- Single instance prevents resource exhaustion
- CSP disabled for dev, will configure for prod
- Update checker uses secure HTTPS channel
```
