# Research Report: Desktop App UI/UX Design Patterns

**Research Date:** 2026-01-17
**Topics:** Glassmorphism, Neon Themes, Light/Dark Mode, System Tray Icons, Dashboard Widgets

## Executive Summary

Modern desktop apps prioritize glassmorphism + dark mode for aesthetic depth, neon accents for status indicators, and compact widgets for real-time updates. Tauri supports all patterns via CSS + system tray APIs. Use `backdrop-filter: blur()` for glass effects, `text-shadow` layering for neon glow, `prefers-color-scheme` for system detection, and SVG icons for tray percentage indicators.

## Key Findings

### 1. Glassmorphism Implementation

**Core CSS Pattern:**

```css
.glass {
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  border-radius: 16px;
  border: 1px solid rgba(255, 255, 255, 0.2);
  box-shadow: 0 8px 32px rgba(31, 38, 135, 0.37);
}
```

**Key Parameters:**

- Blur range: 8px–15px (8px = subtle, 15px = heavy diffusion)
- Background opacity: 0.05–0.3 for white; 0.1–0.2 for colored backgrounds
- Border: 1px solid with 0.2 opacity white creates frosted frame
- Shadow: Soft 8px blur + 32px spread for depth

**Browser Support:** Chrome 76+, Safari 9+, Firefox 103+. Always use `-webkit-` prefix for Safari compatibility.

**Accessibility:** Maintain 4.5:1 contrast for normal text. Increase opacity to 0.3–0.4 or add text-shadow if needed.

### 2. Neon Theme Design

**Glow Effect (Text):**

```css
.neon-text {
  color: #00e5ff;
  text-shadow:
    0 0 8px #00e5ff,
    0 0 12px #00e5ff,
    0 0 20px #ff00ff,
    0 0 40px #ff00ff;
  font-weight: bold;
}
```

**Glow Effect (Box):**

```css
.neon-box {
  background: rgba(5, 8, 26, 1);
  border: 2px solid #00e5ff;
  box-shadow:
    0 0 10px #00e5ff,
    inset 0 0 10px rgba(0, 229, 255, 0.1);
}
```

**Recommended Palettes:**

- **Cyberpunk:** Cyan (#00e5ff) + Magenta (#ff00ff) + Neon Green (#00ff85) on Navy (#05081a)
- **Hacker:** Pure Green (#39ff14) + Cyan (#00e5ff) on Black
- **Vaporwave:** Hot Pink (#ff0054) + Cyan (#00e5ff) + Purple (#b100ff) on Deep Navy

**Best Practice:** Neon on dark backgrounds only. Avoid neon-on-neon combinations; use high-contrast pairings.

### 3. Light/Dark Mode Implementation

**CSS Media Query Approach:**

```css
:root {
  color-scheme: light dark;
}

@media (prefers-color-scheme: light) {
  :root {
    --bg-primary: #ffffff;
    --text-primary: #1a1a1a;
  }
}

@media (prefers-color-scheme: dark) {
  :root {
    --bg-primary: #1a1a1a;
    --text-primary: #ffffff;
  }
}

body {
  background-color: var(--bg-primary);
  color: var(--text-primary);
  transition:
    background-color 0.3s ease,
    color 0.3s ease;
}

@media (prefers-reduced-motion: reduce) {
  * {
    transition: none !important;
  }
}
```

**Modern `light-dark()` Function:**

```css
body {
  background: light-dark(#fff, #1a1a1a);
  color: light-dark(#000, #fff);
}
```

**System Detection:** Browser auto-detects OS preferences. Override via localStorage for manual toggle (three-state: system/light/dark).

### 4. System Tray Icon Design

**Dynamic Percentage Icon (SVG Approach):**

```javascript
// Generate SVG tray icon with percentage fill
function generateTrayIcon(percentage) {
  const radius = 45;
  const circumference = 2 * Math.PI * radius;
  const strokeDashoffset = circumference - (percentage / 100) * circumference;

  const svg = `
    <svg viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
      <circle cx="50" cy="50" r="${radius}" fill="none" stroke="#333" stroke-width="4"/>
      <circle cx="50" cy="50" r="${radius}" fill="none" stroke="#00e5ff"
              stroke-width="4" stroke-dasharray="${circumference}"
              stroke-dashoffset="${strokeDashoffset}"
              stroke-linecap="round" transform="rotate(-90 50 50)"/>
      <text x="50" y="58" text-anchor="middle" font-size="24" font-weight="bold" fill="#00e5ff">
        ${percentage}%
      </text>
    </svg>
  `;
  return svg;
}
```

**Icon States:**

- 0–33%: Green (#39ff14)
- 34–66%: Yellow (#ffff00)
- 67–99%: Orange (#ff8800)
- 100%: Red (#ff0000) with warning indicator

**Tauri Integration:** Use `tray::TrayIconBuilder` to update icon dynamically via `set_icon()` API.

**Dark/Light Adaptability:** Export icons in both color schemes. Detect system theme and switch accordingly.

### 5. Compact Dashboard Widget (Usage Percentage + Reset Time)

**HTML Structure:**

```html
<div class="dashboard-widget glass">
  <div class="header">
    <h3>Claude Usage</h3>
    <span class="reset-time">Resets in 4h 23m</span>
  </div>
  <div class="usage-bar">
    <div class="fill" style="width: 72%"></div>
    <span class="percentage">72%</span>
  </div>
  <div class="stats">
    <div class="stat">
      <span class="label">Requests:</span>
      <span class="value">720/1000</span>
    </div>
    <div class="stat">
      <span class="label">Tokens:</span>
      <span class="value">2.4M/5M</span>
    </div>
  </div>
</div>
```

**CSS Styling (Compact + Glass Effect):**

```css
.dashboard-widget {
  width: 280px;
  padding: 16px;
  background: rgba(255, 255, 255, 0.08);
  backdrop-filter: blur(10px);
  border-radius: 12px;
  border: 1px solid rgba(255, 255, 255, 0.15);
  font-family: system-ui, sans-serif;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.header h3 {
  margin: 0;
  font-size: 14px;
  font-weight: 600;
}

.reset-time {
  font-size: 12px;
  opacity: 0.7;
}

.usage-bar {
  position: relative;
  height: 20px;
  background: rgba(0, 0, 0, 0.2);
  border-radius: 10px;
  overflow: hidden;
  margin-bottom: 8px;
}

.usage-bar .fill {
  height: 100%;
  background: linear-gradient(90deg, #00e5ff, #ff00ff);
  transition: width 0.3s ease;
}

.usage-bar .percentage {
  position: absolute;
  right: 8px;
  top: 50%;
  transform: translateY(-50%);
  font-size: 11px;
  font-weight: bold;
  color: white;
  text-shadow: 0 0 4px rgba(0, 0, 0, 0.5);
}

.stats {
  display: flex;
  flex-direction: column;
  gap: 6px;
  font-size: 12px;
}

.stat {
  display: flex;
  justify-content: space-between;
}

.stat .label {
  opacity: 0.7;
}
.stat .value {
  font-weight: 600;
  color: #00e5ff;
}
```

**Responsive:** Fixed 280px width fits standard tray dock. Stack stats vertically for small screens.

## Design Recommendations

1. **Glass + Dark Mode:** Default combo reduces eye strain, provides modern aesthetic
2. **Neon Accents:** Use only for status indicators (active/warning/error), not primary UI
3. **SVG Tray Icons:** Scalable, theme-aware, support smooth percentage animations
4. **One Metric Per Widget:** Dashboard shows usage % + reset time only; drill-down for details
5. **Tauri Compatibility:** All patterns work with Tauri's CSS + system tray APIs

## Code References

- [Glassmorphism Generator](https://css.glass/)
- [Neon Color Tools](https://www.terrific.tools/color/neon-color-generator/)
- [prefers-color-scheme MDN](https://developer.mozilla.org/en-US/docs/Web/CSS/@media/prefers-color-scheme)
- [Tauri System Tray Docs](https://v2.tauri.app/learn/system-tray/)
- [Microsoft Widget Design](https://learn.microsoft.com/en-us/windows/apps/design/widgets/)

## Unresolved Questions

- Tauri support for animated tray icon updates (need to verify frame rate limits)
- Performance impact of continuous SVG re-rendering for tray icon percentage changes
- Dark mode auto-detection behavior on Linux (GNOME vs KDE vs others)
