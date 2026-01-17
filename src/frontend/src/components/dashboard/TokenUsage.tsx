import { motion } from "framer-motion";
import styles from "./TokenUsage.module.css";

interface TokenUsageProps {
  inputUsed: number;
  inputLimit: number;
  outputUsed: number;
  outputLimit: number;
}

function formatTokens(num: number): string {
  if (num >= 1000000) return `${(num / 1000000).toFixed(1)}M`;
  if (num >= 1000) return `${(num / 1000).toFixed(0)}K`;
  return num.toString();
}

export function TokenUsage({
  inputUsed,
  inputLimit,
  outputUsed,
  outputLimit,
}: TokenUsageProps) {
  const inputPercent = Math.min((inputUsed / inputLimit) * 100, 100);
  const outputPercent = Math.min((outputUsed / outputLimit) * 100, 100);

  return (
    <div className={styles.container}>
      <motion.div
        className={styles.row}
        initial={{ opacity: 0, x: -10 }}
        animate={{ opacity: 1, x: 0 }}
        transition={{ delay: 0.1 }}
      >
        <div className={styles.label}>Input</div>
        <div className={styles.bar}>
          <motion.div
            className={styles.fill}
            initial={{ width: 0 }}
            animate={{ width: `${inputPercent}%` }}
            transition={{ duration: 0.6, ease: "easeOut" }}
          />
        </div>
        <div className={styles.value}>{formatTokens(inputUsed)}</div>
      </motion.div>

      <motion.div
        className={styles.row}
        initial={{ opacity: 0, x: -10 }}
        animate={{ opacity: 1, x: 0 }}
        transition={{ delay: 0.2 }}
      >
        <div className={styles.label}>Output</div>
        <div className={styles.bar}>
          <motion.div
            className={`${styles.fill} ${styles.fillSecondary}`}
            initial={{ width: 0 }}
            animate={{ width: `${outputPercent}%` }}
            transition={{ duration: 0.6, ease: "easeOut", delay: 0.1 }}
          />
        </div>
        <div className={styles.value}>{formatTokens(outputUsed)}</div>
      </motion.div>
    </div>
  );
}
