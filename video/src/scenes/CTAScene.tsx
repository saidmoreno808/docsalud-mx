import { AbsoluteFill, interpolate, spring, useCurrentFrame, useVideoConfig } from "remotion";

const BRAND = "#00C4A1";
const ACCENT = "#6366F1";
const BG = "#0a0e1a";

interface LinkBadgeProps {
  icon: string;
  label: string;
  value: string;
  color: string;
  delay: number;
}

const LinkBadge = ({ icon, label, value, color, delay }: LinkBadgeProps) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const sp = spring({ frame: frame - delay, fps, config: { damping: 14, stiffness: 130 } });
  const opacity = interpolate(frame - delay, [0, 10], [0, 1], { extrapolateRight: "clamp", extrapolateLeft: "clamp" });
  const y = interpolate(sp, [0, 1], [30, 0]);

  return (
    <div style={{
      opacity,
      transform: `translateY(${y}px)`,
      background: `${color}10`,
      border: `1px solid ${color}40`,
      borderRadius: 14,
      padding: "20px 28px",
      display: "flex",
      alignItems: "center",
      gap: 18,
    }}>
      <span style={{ fontSize: 32 }}>{icon}</span>
      <div>
        <div style={{
          fontSize: 13,
          color: "#64748b",
          fontFamily: "system-ui, -apple-system, sans-serif",
          textTransform: "uppercase",
          letterSpacing: 0.5,
          marginBottom: 4,
        }}>
          {label}
        </div>
        <div style={{
          fontSize: 18,
          fontWeight: 700,
          color,
          fontFamily: "monospace",
        }}>
          {value}
        </div>
      </div>
    </div>
  );
};

export const CTAScene = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  // Title entrance
  const titleSp = spring({ frame, fps, config: { damping: 14, stiffness: 100 } });
  const titleScale = interpolate(titleSp, [0, 1], [0.8, 1]);
  const titleOpacity = interpolate(frame, [0, 15], [0, 1], { extrapolateRight: "clamp" });

  // Subtitle
  const subOpacity = interpolate(frame, [fps * 0.5, fps * 1], [0, 1], { extrapolateRight: "clamp", extrapolateLeft: "clamp" });

  // Glow pulse
  const glow = interpolate(Math.sin((frame / fps) * 2 * Math.PI * 0.6), [-1, 1], [0.4, 1.0]);

  return (
    <AbsoluteFill style={{ background: BG, display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center", padding: "80px 120px" }}>
      {/* Background radials */}
      <div style={{
        position: "absolute", top: "5%", left: "20%",
        width: 700, height: 700, borderRadius: "50%",
        background: `radial-gradient(circle, ${BRAND}12 0%, transparent 65%)`,
      }} />
      <div style={{
        position: "absolute", bottom: "5%", right: "15%",
        width: 500, height: 500, borderRadius: "50%",
        background: `radial-gradient(circle, ${ACCENT}12 0%, transparent 65%)`,
      }} />

      {/* Main heading */}
      <div style={{
        opacity: titleOpacity,
        transform: `scale(${titleScale})`,
        textAlign: "center",
        marginBottom: 20,
      }}>
        <h1 style={{
          margin: 0,
          fontSize: 72,
          fontWeight: 900,
          fontFamily: "system-ui, -apple-system, sans-serif",
          background: `linear-gradient(135deg, ${BRAND}, ${ACCENT})`,
          WebkitBackgroundClip: "text",
          WebkitTextFillColor: "transparent",
          lineHeight: 1.1,
          filter: `drop-shadow(0 0 40px ${BRAND}${Math.round(glow * 80).toString(16).padStart(2, "0")})`,
        }}>
          ClinicaIA
        </h1>
      </div>

      {/* Subtitle */}
      <div style={{ opacity: subOpacity, textAlign: "center", marginBottom: 56 }}>
        <p style={{
          margin: 0,
          fontSize: 26,
          color: "#94a3b8",
          fontFamily: "system-ui, -apple-system, sans-serif",
          lineHeight: 1.5,
        }}>
          From paper records to AI-assisted diagnosis<br />
          <span style={{ color: "#f1f5f9", fontWeight: 600 }}>in under 5 seconds</span>
        </p>
      </div>

      {/* Links */}
      <div style={{ display: "flex", flexDirection: "column", gap: 20, width: "100%", maxWidth: 760, marginBottom: 52 }}>
        <LinkBadge icon="🌐" label="Live demo" value="clinicaia-docsalud-tk3ds.ondigitalocean.app" color={BRAND} delay={fps * 1.0} />
        <LinkBadge icon="💻" label="Source code" value="github.com/saidmoreno808/docsalud-mx" color={ACCENT} delay={fps * 1.3} />
        <LinkBadge icon="🏆" label="Hackathon" value="DigitalOcean Gradient AI Hackathon — March 2026" color="#F59E0B" delay={fps * 1.6} />
      </div>

      {/* Built with DO badge */}
      <div style={{
        opacity: interpolate(frame - fps * 2, [0, 20], [0, 1], { extrapolateRight: "clamp", extrapolateLeft: "clamp" }),
        display: "flex",
        alignItems: "center",
        gap: 14,
        background: "rgba(255,255,255,0.04)",
        border: "1px solid rgba(255,255,255,0.1)",
        borderRadius: 50,
        padding: "14px 32px",
      }}>
        <svg width={32} height={32} viewBox="0 0 32 32">
          <circle cx={16} cy={16} r={16} fill="#0080FF" />
          <text x={16} y={22} textAnchor="middle" fill="white" fontSize={16} fontWeight={900} fontFamily="system-ui">do</text>
        </svg>
        <span style={{
          fontSize: 18,
          color: "#e2e8f0",
          fontFamily: "system-ui, -apple-system, sans-serif",
          fontWeight: 500,
        }}>
          Powered by <strong style={{ color: "#0080FF" }}>DigitalOcean</strong> · Gradient AI · App Platform · Managed PG
        </span>
      </div>
    </AbsoluteFill>
  );
};
