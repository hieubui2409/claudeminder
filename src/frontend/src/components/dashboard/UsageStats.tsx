import { motion } from "framer-motion";
import { useEffect, useState } from "react";
import styles from "./UsageStats.module.css";

interface UsageStatsProps {
  stats: {
    sessionsToday: number;
    avgDuration: string;
    peakHour: string;
    totalQueries: number;
  };
}

function AnimatedNumber({ value }: { value: number }) {
  const [displayValue, setDisplayValue] = useState(0);

  useEffect(() => {
    let start = 0;
    const duration = 800; // ms
    const increment = value / (duration / 16); // 60fps

    const timer = setInterval(() => {
      start += increment;
      if (start >= value) {
        setDisplayValue(value);
        clearInterval(timer);
      } else {
        setDisplayValue(Math.floor(start));
      }
    }, 16);

    return () => clearInterval(timer);
  }, [value]);

  return <>{displayValue}</>;
}

export function UsageStats({ stats }: UsageStatsProps) {
  return (
    <div className={styles.grid}>
      <motion.div
        className={styles.stat}
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.1 }}
      >
        <div className={styles.statValue}>
          <AnimatedNumber value={stats.sessionsToday} />
        </div>
        <div className={styles.statLabel}>Sessions</div>
      </motion.div>

      <motion.div
        className={styles.stat}
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.2 }}
      >
        <div className={styles.statValue}>{stats.avgDuration}</div>
        <div className={styles.statLabel}>Avg Time</div>
      </motion.div>

      <motion.div
        className={styles.stat}
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.3 }}
      >
        <div className={styles.statValue}>{stats.peakHour}</div>
        <div className={styles.statLabel}>Peak</div>
      </motion.div>

      <motion.div
        className={styles.stat}
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.4 }}
      >
        <div className={styles.statValue}>
          {stats.totalQueries >= 1000
            ? `${(stats.totalQueries / 1000).toFixed(0)}K`
            : stats.totalQueries}
        </div>
        <div className={styles.statLabel}>Tokens</div>
      </motion.div>
    </div>
  );
}
