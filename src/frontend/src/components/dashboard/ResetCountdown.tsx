import { useEffect, useState } from "react";
import styles from "./ResetCountdown.module.css";

interface ResetCountdownProps {
  resetTime: Date; // Target reset time
  onReset?: () => void; // Callback when reset occurs
  compact?: boolean; // Compact mode for header
}

function formatTime(ms: number): string {
  const totalSeconds = Math.floor(ms / 1000);
  const hours = Math.floor(totalSeconds / 3600);
  const minutes = Math.floor((totalSeconds % 3600) / 60);
  const seconds = totalSeconds % 60;

  // If more than 1 hour, show "Xh Ym"
  if (hours > 0) {
    return `${hours}h ${minutes}m`;
  }

  // If less than 1 hour, show "Xm Ys" format consistently
  if (minutes > 0) {
    return `${minutes}m ${seconds}s`;
  }

  // Less than 1 minute, show seconds only
  return `${seconds}s`;
}

export function ResetCountdown({
  resetTime,
  onReset,
  compact = false,
}: ResetCountdownProps) {
  const [timeLeft, setTimeLeft] = useState<number>(0);
  const [hasReset, setHasReset] = useState(false);

  useEffect(() => {
    const calculateTimeLeft = () => {
      const now = new Date().getTime();
      const target = new Date(resetTime).getTime();
      const diff = target - now;

      if (diff <= 0 && !hasReset) {
        setHasReset(true);
        onReset?.();
        return 0;
      }

      return Math.max(0, diff);
    };

    // Initial calculation
    setTimeLeft(calculateTimeLeft());

    // Update every second
    const interval = setInterval(() => {
      setTimeLeft(calculateTimeLeft());
    }, 1000);

    return () => clearInterval(interval);
  }, [resetTime, onReset, hasReset]);

  const isUrgent = timeLeft > 0 && timeLeft < 5 * 60 * 1000; // Less than 5 minutes
  const containerClasses = [
    styles.container,
    compact ? styles.compact : "",
    isUrgent ? styles.urgent : "",
  ]
    .filter(Boolean)
    .join(" ");

  return (
    <div className={containerClasses}>
      <div className={styles.time}>{formatTime(timeLeft)}</div>
      <div className={styles.label}>Until Reset</div>
    </div>
  );
}
