import React from "react";
import "./glow-text.css";

export interface GlowTextProps {
  children: React.ReactNode;
  className?: string;
  color?: "accent" | "success" | "warning" | "danger" | "gradient" | "custom";
  customColor?: string;
  intensity?: "low" | "medium" | "high";
  animated?: boolean;
  as?: "h1" | "h2" | "h3" | "h4" | "h5" | "h6" | "p" | "span";
}

export const GlowText: React.FC<GlowTextProps> = ({
  children,
  className = "",
  color = "accent",
  customColor,
  intensity = "medium",
  animated = false,
  as: Component = "span",
}) => {
  const colorClass = customColor ? "" : `glow-text--${color}`;
  const intensityClass = color === "gradient" ? "" : `glow-text--${intensity}`;
  const animatedClass = animated ? "glow-text--animated" : "";

  const style = customColor
    ? ({ "--glow-color": customColor } as React.CSSProperties)
    : undefined;

  return (
    <Component
      className={`glow-text ${colorClass} ${intensityClass} ${animatedClass} ${className}`.trim()}
      style={style}
    >
      {children}
    </Component>
  );
};

// Re-export with old name for backwards compatibility
export { GlowText as NeonText };
export type { GlowTextProps as NeonTextProps };
