import React, { useMemo } from "react";
import "./gauge-progress.css";

export interface GaugeProgressProps {
  percentage: number;
  size?: number;
  className?: string;
  showValue?: boolean;
  label?: string;
  animated?: boolean;
}

/**
 * Gauge/speedometer style progress indicator.
 * Arc from 0-180 degrees with gradient from green to yellow to red.
 * Needle rotates based on percentage value.
 */
export const GaugeProgress: React.FC<GaugeProgressProps> = ({
  percentage,
  size = 200,
  className = "",
  showValue = true,
  label,
  animated = true,
}) => {
  const normalizedPercentage = Math.min(Math.max(percentage, 0), 100);

  // Calculate needle rotation (0% = -90deg, 100% = 90deg)
  const needleRotation = -90 + (normalizedPercentage / 100) * 180;

  // SVG dimensions
  const strokeWidth = size * 0.08;
  const radius = (size - strokeWidth) / 2;
  const centerX = size / 2;
  const centerY = size / 2;

  // Create arc path (semicircle from -90deg to 90deg)
  const arcPath = useMemo(() => {
    const startAngle = -Math.PI / 2; // -90deg
    const endAngle = Math.PI / 2; // 90deg

    const startX = centerX + radius * Math.cos(startAngle);
    const startY = centerY + radius * Math.sin(startAngle);
    const endX = centerX + radius * Math.cos(endAngle);
    const endY = centerY + radius * Math.sin(endAngle);

    return `M ${startX} ${startY} A ${radius} ${radius} 0 0 1 ${endX} ${endY}`;
  }, [centerX, centerY, radius]);

  // Gradient stops for green -> yellow -> red
  const gradientId = `gauge-gradient-${Math.random().toString(36).substr(2, 9)}`;

  const animatedClass = animated ? "gauge-progress--animated" : "";

  return (
    <div className={`gauge-progress ${animatedClass} ${className}`}>
      <svg width={size} height={size * 0.65} className="gauge-progress__svg">
        <defs>
          {/* Gradient definition */}
          <linearGradient id={gradientId} x1="0%" y1="0%" x2="100%" y2="0%">
            <stop offset="0%" stopColor="var(--success, #22c55e)" />
            <stop offset="50%" stopColor="var(--warning, #f59e0b)" />
            <stop offset="100%" stopColor="var(--danger, #ef4444)" />
          </linearGradient>
        </defs>

        {/* Background arc */}
        <path
          className="gauge-progress__background"
          d={arcPath}
          strokeWidth={strokeWidth}
          fill="none"
        />

        {/* Progress arc */}
        <path
          className="gauge-progress__arc"
          d={arcPath}
          strokeWidth={strokeWidth}
          fill="none"
          stroke={`url(#${gradientId})`}
          strokeDasharray={Math.PI * radius}
          strokeDashoffset={Math.PI * radius * (1 - normalizedPercentage / 100)}
        />

        {/* Needle */}
        <g
          className="gauge-progress__needle"
          transform={`rotate(${needleRotation} ${centerX} ${centerY})`}
        >
          <line
            x1={centerX}
            y1={centerY}
            x2={centerX + radius * 0.7}
            y2={centerY}
            strokeWidth={strokeWidth * 0.3}
            stroke="var(--text-primary, #1a1a1a)"
            strokeLinecap="round"
          />
          {/* Center dot */}
          <circle
            cx={centerX}
            cy={centerY}
            r={strokeWidth * 0.5}
            fill="var(--text-primary, #1a1a1a)"
          />
        </g>
      </svg>

      {/* Value and label */}
      {(showValue || label) && (
        <div className="gauge-progress__info">
          {showValue && (
            <div className="gauge-progress__value">
              {normalizedPercentage.toFixed(0)}
              <span className="gauge-progress__symbol">%</span>
            </div>
          )}
          {label && <div className="gauge-progress__label">{label}</div>}
        </div>
      )}
    </div>
  );
};
