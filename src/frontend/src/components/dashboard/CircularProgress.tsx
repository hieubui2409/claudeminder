import { motion } from "framer-motion";
import styles from "./CircularProgress.module.css";

interface CircularProgressProps {
  value: number; // 0-100
  size?: "sm" | "md" | "lg";
  showLabel?: boolean;
  label?: string;
  color?: "default" | "success" | "warning" | "error";
  animated?: boolean;
}

const sizeMap = {
  sm: 80,
  md: 120,
  lg: 180,
};

const strokeWidthMap = {
  sm: 6,
  md: 8,
  lg: 10,
};

export function CircularProgress({
  value,
  size = "md",
  showLabel = true,
  label,
  color = "default",
  animated = true,
}: CircularProgressProps) {
  // Clamp value between 0 and 100
  const clampedValue = Math.max(0, Math.min(100, value));
  const diameter = sizeMap[size];
  const strokeWidth = strokeWidthMap[size];
  const radius = (diameter - strokeWidth) / 2;
  const circumference = radius * 2 * Math.PI;
  const offset = circumference - (clampedValue / 100) * circumference;

  const sizeClass = `size${size.charAt(0).toUpperCase() + size.slice(1)}`;
  const colorClass =
    color !== "default"
      ? `color${color.charAt(0).toUpperCase() + color.slice(1)}`
      : "";
  const containerClasses = [
    styles.container,
    styles[sizeClass],
    colorClass ? styles[colorClass] : "",
  ]
    .filter(Boolean)
    .join(" ");

  return (
    <div className={containerClasses}>
      <svg
        width={diameter}
        height={diameter}
        className={styles.svg}
        viewBox={`0 0 ${diameter} ${diameter}`}
      >
        {/* Background track */}
        <circle
          className={styles.trackCircle}
          cx={diameter / 2}
          cy={diameter / 2}
          r={radius}
          strokeWidth={strokeWidth}
        />

        {/* Progress circle */}
        {animated ? (
          <motion.circle
            className={styles.progressCircle}
            cx={diameter / 2}
            cy={diameter / 2}
            r={radius}
            strokeWidth={strokeWidth}
            strokeDasharray={circumference}
            initial={{ strokeDashoffset: circumference }}
            animate={{ strokeDashoffset: offset }}
            transition={{ duration: 0.8, ease: "easeOut" }}
          />
        ) : (
          <circle
            className={styles.progressCircle}
            cx={diameter / 2}
            cy={diameter / 2}
            r={radius}
            strokeWidth={strokeWidth}
            strokeDasharray={circumference}
            strokeDashoffset={offset}
          />
        )}
      </svg>

      {showLabel && (
        <div className={styles.label}>
          <motion.span
            className={styles.value}
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.3 }}
          >
            {Math.round(clampedValue)}%
          </motion.span>
          {label && <span className={styles.sublabel}>{label}</span>}
        </div>
      )}
    </div>
  );
}
