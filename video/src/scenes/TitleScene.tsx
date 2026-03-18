import { AbsoluteFill, interpolate, spring, useCurrentFrame, useVideoConfig } from "remotion";

const BRAND = "#00C4A1";
const ACCENT = "#6366F1";
const BG = "#0a0e1a";

export const TitleScene = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  // Logo entrance
  const logoScale = spring({ frame, fps, config: { damping: 12, stiffness: 120 } });
  const logoOpacity = interpolate(frame, [0, 15], [0, 1], { extrapolateRight: "clamp" });

  // Tagline slides up
  const taglineY = interpolate(
    spring({ frame: frame - fps * 0.6, fps, config: { damping: 200 } }),
    [0, 1], [60, 0]
  );
  const taglineOpacity = interpolate(frame, [fps * 0.6, fps * 1.1], [0, 1], { extrapolateRight: "clamp", extrapolateLeft: "clamp" });

  // Sub-text fade in
  const subOpacity = interpolate(frame, [fps * 1.4, fps * 2], [0, 1], { extrapolateRight: "clamp", extrapolateLeft: "clamp" });

  // DO badge fade in
  const badgeOpacity = interpolate(frame, [fps * 2.2, fps * 3], [0, 1], { extrapolateRight: "clamp", extrapolateLeft: "clamp" });
  const badgeY = interpolate(frame, [fps * 2.2, fps * 3], [20, 0], { extrapolateRight: "clamp", extrapolateLeft: "clamp" });

  // Glowing pulse on brand name (subtle oscillation)
  const glow = interpolate(Math.sin((frame / fps) * 2 * Math.PI * 0.5), [-1, 1], [0.6, 1.0]);

  return (
    <AbsoluteFill style={{ background: BG, display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center" }}>
      {/* Background gradient circles */}
      <div style={{
        position: "absolute", top: "10%", left: "15%",
        width: 600, height: 600, borderRadius: "50%",
        background: `radial-gradient(circle, ${BRAND}18 0%, transparent 70%)`,
      }} />
      <div style={{
        position: "absolute", bottom: "10%", right: "10%",
        width: 500, height: 500, borderRadius: "50%",
        background: `radial-gradient(circle, ${ACCENT}18 0%, transparent 70%)`,
      }} />

      {/* Logo + brand */}
      <div style={{ opacity: logoOpacity, transform: `scale(${logoScale})`, display: "flex", alignItems: "center", gap: 24, marginBottom: 32 }}>
        {/* Medical cross icon */}
        <svg width={80} height={80} viewBox="0 0 80 80">
          <rect x={28} y={8} width={24} height={64} rx={6} fill={BRAND} opacity={glow} />
          <rect x={8} y={28} width={64} height={24} rx={6} fill={BRAND} opacity={glow} />
          <rect x={28} y={8} width={24} height={64} rx={6} fill={`${BRAND}50`} />
          <rect x={8} y={28} width={64} height={24} rx={6} fill={`${BRAND}50`} />
        </svg>

        <span style={{
          fontSize: 96,
          fontWeight: 900,
          fontFamily: "system-ui, -apple-system, sans-serif",
          background: `linear-gradient(135deg, ${BRAND}, ${ACCENT})`,
          WebkitBackgroundClip: "text",
          WebkitTextFillColor: "transparent",
          letterSpacing: -2,
        }}>
          ClinicaIA
        </span>
      </div>

      {/* Tagline */}
      <div style={{ opacity: taglineOpacity, transform: `translateY(${taglineY}px)`, marginBottom: 24 }}>
        <p style={{
          fontSize: 38,
          fontWeight: 600,
          color: "#e2e8f0",
          fontFamily: "system-ui, -apple-system, sans-serif",
          textAlign: "center",
          margin: 0,
          letterSpacing: -0.5,
        }}>
          Artificial Intelligence for the Clinical Record
        </p>
      </div>

      {/* Sub text */}
      <div style={{ opacity: subOpacity, marginBottom: 48 }}>
        <p style={{
          fontSize: 24,
          color: "#94a3b8",
          fontFamily: "system-ui, -apple-system, sans-serif",
          textAlign: "center",
          margin: 0,
        }}>
          OCR · NLP · RAG · LLM — from paper to diagnosis in seconds
        </p>
      </div>

      {/* DO Gradient AI badge */}
      <div style={{
        opacity: badgeOpacity,
        transform: `translateY(${badgeY}px)`,
        display: "flex",
        alignItems: "center",
        gap: 12,
        background: "rgba(255,255,255,0.06)",
        border: `1px solid ${BRAND}50`,
        borderRadius: 50,
        padding: "12px 28px",
      }}>
        {/* DO logo simplified */}
        <svg width={28} height={28} viewBox="0 0 28 28">
          <circle cx={14} cy={14} r={14} fill="#0080FF" />
          <text x={14} y={19} textAnchor="middle" fill="white" fontSize={14} fontWeight={900} fontFamily="system-ui">do</text>
        </svg>
        <span style={{ color: "#e2e8f0", fontSize: 20, fontWeight: 600, fontFamily: "system-ui, -apple-system, sans-serif" }}>
          DigitalOcean Gradient AI Hackathon 2026
        </span>
      </div>
    </AbsoluteFill>
  );
};
