import { AbsoluteFill, interpolate, spring, useCurrentFrame, useVideoConfig } from "remotion";

const BRAND = "#00C4A1";
const ACCENT = "#6366F1";
const DANGER = "#EF4444";
const BG = "#0a0e1a";

interface StatCardProps {
  value: string;
  label: string;
  color: string;
  delay: number;
}

const StatCard = ({ value, label, color, delay }: StatCardProps) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const sp = spring({ frame: frame - delay, fps, config: { damping: 14, stiffness: 100 } });
  const opacity = interpolate(frame - delay, [0, 10], [0, 1], { extrapolateRight: "clamp", extrapolateLeft: "clamp" });
  const y = interpolate(sp, [0, 1], [50, 0]);

  return (
    <div style={{
      opacity,
      transform: `translateY(${y}px)`,
      background: "rgba(255,255,255,0.05)",
      border: `1px solid ${color}40`,
      borderRadius: 16,
      padding: "32px 40px",
      textAlign: "center",
      minWidth: 260,
      boxShadow: `0 0 40px ${color}20`,
    }}>
      <div style={{
        fontSize: 64,
        fontWeight: 900,
        fontFamily: "system-ui, -apple-system, sans-serif",
        color,
        lineHeight: 1,
        marginBottom: 12,
      }}>
        {value}
      </div>
      <div style={{
        fontSize: 20,
        color: "#94a3b8",
        fontFamily: "system-ui, -apple-system, sans-serif",
        lineHeight: 1.4,
      }}>
        {label}
      </div>
    </div>
  );
};

interface ProblemItemProps {
  text: string;
  delay: number;
}

const ProblemItem = ({ text, delay }: ProblemItemProps) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const opacity = interpolate(frame - delay, [0, 15], [0, 1], { extrapolateRight: "clamp", extrapolateLeft: "clamp" });
  const x = interpolate(frame - delay, [0, 20], [-40, 0], { extrapolateRight: "clamp", extrapolateLeft: "clamp" });

  return (
    <div style={{
      opacity,
      transform: `translateX(${x}px)`,
      display: "flex",
      alignItems: "flex-start",
      gap: 16,
      marginBottom: 20,
    }}>
      <div style={{
        width: 10, height: 10, borderRadius: "50%",
        background: DANGER,
        marginTop: 8,
        flexShrink: 0,
        boxShadow: `0 0 12px ${DANGER}`,
      }} />
      <p style={{
        margin: 0,
        fontSize: 22,
        color: "#cbd5e1",
        fontFamily: "system-ui, -apple-system, sans-serif",
        lineHeight: 1.5,
      }}>
        {text}
      </p>
    </div>
  );
};

export const ProblemScene = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const titleOpacity = interpolate(frame, [0, 20], [0, 1], { extrapolateRight: "clamp" });
  const titleY = interpolate(frame, [0, 20], [-30, 0], { extrapolateRight: "clamp" });

  return (
    <AbsoluteFill style={{ background: BG, padding: "80px 120px", display: "flex", flexDirection: "column" }}>
      {/* Background radial */}
      <div style={{
        position: "absolute", top: 0, left: 0, right: 0, bottom: 0,
        background: `radial-gradient(ellipse at 80% 20%, ${DANGER}0D 0%, transparent 60%)`,
      }} />

      {/* Title */}
      <div style={{ opacity: titleOpacity, transform: `translateY(${titleY}px)`, marginBottom: 56 }}>
        <div style={{
          display: "inline-flex",
          alignItems: "center",
          gap: 16,
          background: `${DANGER}15`,
          border: `1px solid ${DANGER}40`,
          borderRadius: 8,
          padding: "8px 20px",
          marginBottom: 20,
        }}>
          <span style={{ fontSize: 18, color: DANGER, fontWeight: 700, fontFamily: "system-ui, -apple-system, sans-serif" }}>
            THE PROBLEM
          </span>
        </div>
        <h1 style={{
          margin: 0,
          fontSize: 54,
          fontWeight: 800,
          color: "#f1f5f9",
          fontFamily: "system-ui, -apple-system, sans-serif",
          lineHeight: 1.2,
        }}>
          Millions of clinical records<br />
          <span style={{ color: DANGER }}>trapped on paper</span>
        </h1>
      </div>

      {/* Stats row */}
      <div style={{ display: "flex", gap: 32, marginBottom: 56, flexWrap: "wrap" }}>
        <StatCard value="1B+" label="medical records on paper in Mexico" color={DANGER} delay={fps * 0.5} />
        <StatCard value="4.2h" label="average manual digitization per record" color="#F59E0B" delay={fps * 0.8} />
        <StatCard value="34%" label="error rate in manual medical transcription" color={ACCENT} delay={fps * 1.1} />
      </div>

      {/* Problem items */}
      <div>
        <ProblemItem text="Doctors lose hours on administrative tasks instead of treating patients" delay={fps * 1.5} />
        <ProblemItem text="Critical information scattered across multiple documents with no structure or search capability" delay={fps * 1.8} />
        <ProblemItem text="Delayed diagnoses due to inability to instantly access the complete clinical history" delay={fps * 2.1} />
      </div>
    </AbsoluteFill>
  );
};
