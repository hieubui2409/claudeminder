import { motion } from "framer-motion";
import styles from "./GoalsIndicator.module.css";

interface GoalsIndicatorProps {
  current: number; // Current usage count
  goal: number; // Target goal
  period: "daily" | "weekly";
  showTrend?: boolean; // Show up/down arrow
}

function formatNumber(num: number): string {
  if (num >= 1000000) return `${(num / 1000000).toFixed(1)}M`;
  if (num >= 1000) return `${(num / 1000).toFixed(0)}K`;
  return num.toString();
}

export function GoalsIndicator({
  current,
  goal,
  period,
  showTrend = false,
}: GoalsIndicatorProps) {
  const percentage = Math.min((current / goal) * 100, 100);
  const isGoalReached = current >= goal;
  const isAhead = current > goal;

  const containerClasses = [
    styles.container,
    isGoalReached ? styles.goalReached : "",
  ]
    .filter(Boolean)
    .join(" ");

  const getStatusText = () => {
    if (isAhead) return "Ahead of Goal";
    if (isGoalReached) return "Goal Reached!";
    if (percentage >= 80) return "Almost There";
    if (percentage >= 50) return "On Track";
    return "Behind Schedule";
  };

  const getTrendClass = () => {
    if (isAhead) return styles.trendUp;
    if (percentage < 50) return styles.trendDown;
    return "";
  };

  return (
    <div className={containerClasses}>
      <div className={styles.header}>
        <span className={styles.title}>
          {period === "daily" ? "Daily Goal" : "Weekly Goal"}
        </span>
        <span className={styles.stats}>
          {formatNumber(current)} / {formatNumber(goal)}
        </span>
      </div>

      <div className={styles.track}>
        <motion.div
          className={styles.fill}
          initial={{ width: 0 }}
          animate={{ width: `${percentage}%` }}
          transition={{ duration: 0.8, ease: "easeOut" }}
        />
      </div>

      <div className={styles.footer}>
        <span className={styles.status}>{getStatusText()}</span>
        {showTrend && (
          <span className={`${styles.trend} ${getTrendClass()}`}>
            {isAhead ? "↑" : percentage < 50 ? "↓" : "→"}
          </span>
        )}
      </div>
    </div>
  );
}
