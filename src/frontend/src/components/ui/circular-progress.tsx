import React, { useMemo } from "react";
import "./circular-progress.css";

export interface CircularProgressProps {
  percentage: number;
  size?: number;
  strokeWidth?: number;
  className?: string;
  showPercentage?: boolean;
  color?: "accent" | "success" | "warning" | "danger" | "auto";
  animated?: boolean;
}

/**
 * Circular SVG progress indicator with center percentage display.
 * Automatically adjusts color based on usage when color is set to 'auto'.
 */
export const CircularProgress: React.FC<CircularProgressProps> = ({
  percentage,
  size = 120,
  strokeWidth = 8,
  className = "",
  showPercentage = true,
  color = "auto",
  animated = true,
}) => {
  const normalizedPercentage = Math.min(Math.max(percentage, 0), 100);

  const radius = (size - strokeWidth) / 2;
  const circumference = 2 * Math.PI * radius;
  const offset = circumference - (normalizedPercentage / 100) * circumference;

  // Auto color based on percentage
  const progressColor = useMemo(() => {
    if (color !== "auto") {
      return `var(--${color})`;
    }

    if (normalizedPercentage < 50) {
      return "var(--success, #22c55e)";
    } else if (normalizedPercentage < 80) {
      return "var(--warning, #f59e0b)";
    } else {
      return "var(--danger, #ef4444)";
    }
  }, [normalizedPercentage, color]);

  const animatedClass = animated ? "circular-progress--animated" : "";

  return (
    <div className={`circular-progress ${animatedClass} ${className}`}>
      <svg width={size} height={size} className="circular-progress__svg">
        {/* Background circle */}
        <circle
          className="circular-progress__background"
          cx={size / 2}
          cy={size / 2}
          r={radius}
          strokeWidth={strokeWidth}
        />

        {/* Progress circle */}
        <circle
          className="circular-progress__progress"
          cx={size / 2}
          cy={size / 2}
          r={radius}
          strokeWidth={strokeWidth}
          strokeDasharray={circumference}
          strokeDashoffset={offset}
          style={{ stroke: progressColor }}
        />
      </svg>

      {showPercentage && (
        <div className="circular-progress__text">
          <span className="circular-progress__percentage">
            {normalizedPercentage.toFixed(0)}
          </span>
          <span className="circular-progress__symbol">%</span>
        </div>
      )}
    </div>
  );
};
