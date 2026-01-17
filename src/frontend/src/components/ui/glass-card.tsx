import React from "react";
import "./glass-card.css";

export interface GlassCardProps {
  children: React.ReactNode;
  className?: string;
  blur?: "light" | "medium" | "heavy";
  border?: boolean;
  onClick?: () => void;
}

/**
 * Glassmorphism container with backdrop-filter blur effect.
 * Supports three blur levels: light (8px), medium (16px), heavy (24px).
 */
export const GlassCard: React.FC<GlassCardProps> = ({
  children,
  className = "",
  blur = "medium",
  border = true,
  onClick,
}) => {
  const blurClass = `glass-card--blur-${blur}`;
  const borderClass = border ? "glass-card--border" : "";
  const clickableClass = onClick ? "glass-card--clickable" : "";

  return (
    <div
      className={`glass-card ${blurClass} ${borderClass} ${clickableClass} ${className}`}
      onClick={onClick}
    >
      {children}
    </div>
  );
};
