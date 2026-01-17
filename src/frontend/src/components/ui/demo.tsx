import React from "react";
import { GlassCard } from "./glass-card";
import { GlowText } from "./glow-text";
import { CircularProgress } from "./circular-progress";
import { GaugeProgress } from "./gauge-progress";

/**
 * Demo component showcasing all UI components.
 * This file is for development/testing purposes only.
 */
export const UIDemo: React.FC = () => {
  return (
    <div
      style={{
        padding: "2rem",
        display: "flex",
        flexDirection: "column",
        gap: "2rem",
      }}
    >
      <section>
        <h2>Glass Card</h2>
        <div style={{ display: "flex", gap: "1rem", flexWrap: "wrap" }}>
          <GlassCard blur="light">
            <h3>Light Blur</h3>
            <p>8px backdrop filter</p>
          </GlassCard>
          <GlassCard blur="medium">
            <h3>Medium Blur</h3>
            <p>16px backdrop filter</p>
          </GlassCard>
          <GlassCard blur="heavy">
            <h3>Heavy Blur</h3>
            <p>24px backdrop filter</p>
          </GlassCard>
        </div>
      </section>

      <section>
        <h2>Glow Text</h2>
        <div style={{ display: "flex", flexDirection: "column", gap: "1rem" }}>
          <GlowText color="accent" intensity="low">
            Accent Low Intensity
          </GlowText>
          <GlowText color="success" intensity="medium">
            Success Medium Intensity
          </GlowText>
          <GlowText color="warning" intensity="high">
            Warning High Intensity
          </GlowText>
          <GlowText color="danger" intensity="high" animated>
            Danger Animated
          </GlowText>
          <GlowText color="gradient" as="h3">
            Gradient Text Style
          </GlowText>
        </div>
      </section>

      <section>
        <h2>Circular Progress</h2>
        <div style={{ display: "flex", gap: "2rem", flexWrap: "wrap" }}>
          <CircularProgress percentage={25} />
          <CircularProgress percentage={55} />
          <CircularProgress percentage={85} />
          <CircularProgress
            percentage={95}
            color="danger"
            size={150}
            strokeWidth={12}
          />
        </div>
      </section>

      <section>
        <h2>Gauge Progress</h2>
        <div style={{ display: "flex", gap: "2rem", flexWrap: "wrap" }}>
          <GaugeProgress percentage={25} label="Low Usage" />
          <GaugeProgress percentage={55} label="Medium Usage" />
          <GaugeProgress percentage={85} label="High Usage" />
          <GaugeProgress percentage={95} label="Critical" size={250} />
        </div>
      </section>
    </div>
  );
};
