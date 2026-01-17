import { useEffect, useState } from "react";
import { invoke } from "@tauri-apps/api/core";
import { listen } from "@tauri-apps/api/event";
import { getCurrentWindow } from "@tauri-apps/api/window";
import "./styles/overlay.css";

interface UsageData {
  five_hour: {
    utilization: number;
    resets_at: string;
  } | null;
}

function formatResetTime(resetAt: string): string {
  const reset = new Date(resetAt);
  const now = new Date();
  const diffMs = reset.getTime() - now.getTime();

  if (diffMs <= 0) return "Now";

  const hours = Math.floor(diffMs / 3600000);
  const mins = Math.floor((diffMs % 3600000) / 60000);

  if (hours > 0) return `${hours}h ${mins}m`;
  return `${mins}m`;
}

export default function Overlay() {
  const [usage, setUsage] = useState<UsageData | null>(null);

  const fetchUsage = async () => {
    try {
      const data = await invoke<UsageData>("get_usage");
      setUsage(data);
    } catch (err) {
      console.error("Failed to fetch usage:", err);
    }
  };

  useEffect(() => {
    // Mark body as overlay window for CSS overrides
    document.body.classList.add("overlay-window");

    fetchUsage();
    const interval = setInterval(fetchUsage, 30000);

    const setupListener = async () => {
      return await listen("refresh-usage", () => fetchUsage());
    };
    const cleanup = setupListener();

    return () => {
      document.body.classList.remove("overlay-window");
      clearInterval(interval);
      cleanup.then((unlisten) => unlisten());
    };
  }, []);

  const handleDrag = async (e: React.MouseEvent) => {
    if (e.button !== 0) return;
    // Don't drag when clicking close button
    if ((e.target as HTMLElement).closest(".overlay-close")) return;
    // Prevent default to avoid text selection interfering with drag
    e.preventDefault();
    e.stopPropagation();
    try {
      await getCurrentWindow().startDragging();
    } catch (err) {
      console.error("Failed to start dragging:", err);
    }
  };

  const handleClose = async (e: React.MouseEvent) => {
    e.preventDefault();
    e.stopPropagation();
    await invoke("set_overlay_visible", { visible: false });
  };

  const percent = usage?.five_hour?.utilization ?? 0;
  const resetTime = usage?.five_hour?.resets_at
    ? formatResetTime(usage.five_hour.resets_at)
    : "--";

  const getColor = () => {
    if (percent > 80) return "var(--overlay-danger)";
    if (percent > 60) return "var(--overlay-warning)";
    return "var(--overlay-success)";
  };

  return (
    <div className="overlay" onMouseDown={handleDrag} data-tauri-drag-region>
      <button className="overlay-close" onClick={handleClose} title="Close">
        ×
      </button>
      <div className="overlay-content">
        <div className="overlay-percent" style={{ color: getColor() }}>
          {percent.toFixed(0)}%
        </div>
        <div className="overlay-reset">⟲ {resetTime}</div>
      </div>
    </div>
  );
}
