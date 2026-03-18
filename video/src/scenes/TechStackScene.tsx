import { AbsoluteFill, interpolate, spring, useCurrentFrame, useVideoConfig } from "remotion";

const BRAND = "#00C4A1";
const BG = "#0a0e1a";

interface TechItemProps {
  icon: string;
  name: string;
  desc: string;
  color: string;
  delay: number;
}

const TechItem = ({ icon, name, desc, color, delay }: TechItemProps) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const sp = spring({ frame: frame - delay, fps, config: { damping: 14, stiffness: 120 } });
  const opacity = interpolate(frame - delay, [0, 10], [0, 1], { extrapolateRight: "clamp", extrapolateLeft: "clamp" });
  const scale = interpolate(sp, [0, 1], [0.7, 1]);

  return (
    <div style={{
      opacity,
      transform: `scale(${scale})`,
      display: "flex",
      flexDirection: "column",
      alignItems: "center",
      background: `${color}10`,
      border: `1px solid ${color}35`,
      borderRadius: 14,
      padding: "20px 16px",
      width: 165,
      textAlign: "center",
    }}>
      <span style={{ fontSize: 36, marginBottom: 10 }}>{icon}</span>
      <div style={{
        fontSize: 16,
        fontWeight: 700,
        color: "#f1f5f9",
        fontFamily: "system-ui, -apple-system, sans-serif",
        marginBottom: 6,
      }}>
        {name}
      </div>
      <div style={{
        fontSize: 12,
        color: color,
        fontFamily: "system-ui, -apple-system, sans-serif",
        lineHeight: 1.4,
      }}>
        {desc}
      </div>
    </div>
  );
};

export const TechStackScene = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const titleOpacity = interpolate(frame, [0, 20], [0, 1], { extrapolateRight: "clamp" });

  const techItems: TechItemProps[] = [
    { icon: "⚡", name: "FastAPI", desc: "Backend async Python", color: "#10B981", delay: fps * 0.3 },
    { icon: "⚛️", name: "React 18", desc: "Frontend TypeScript", color: "#3B82F6", delay: fps * 0.45 },
    { icon: "🐘", name: "PostgreSQL", desc: "pgvector 384d", color: "#6366F1", delay: fps * 0.6 },
    { icon: "🔍", name: "Tesseract", desc: "Spanish OCR", color: "#F59E0B", delay: fps * 0.75 },
    { icon: "🧠", name: "SpaCy", desc: "NLP/NER es", color: "#8B5CF6", delay: fps * 0.9 },
    { icon: "🤖", name: "Llama 3.3", desc: "DO Gradient AI", color: BRAND, delay: fps * 1.05 },
    { icon: "🐋", name: "Docker", desc: "Compose + NGINX", color: "#0EA5E9", delay: fps * 1.2 },
    { icon: "🌊", name: "DigitalOcean", desc: "App Platform", color: "#0080FF", delay: fps * 1.35 },
  ];

  return (
    <AbsoluteFill style={{ background: BG, padding: "72px 120px", display: "flex", flexDirection: "column" }}>
      {/* Background glow */}
      <div style={{
        position: "absolute", top: "30%", left: "30%",
        width: 800, height: 400,
        background: `radial-gradient(ellipse, ${BRAND}08 0%, transparent 70%)`,
      }} />

      {/* Title */}
      <div style={{ opacity: titleOpacity, marginBottom: 56, textAlign: "center" }}>
        <div style={{
          display: "inline-flex",
          alignItems: "center",
          gap: 12,
          background: `${BRAND}15`,
          border: `1px solid ${BRAND}40`,
          borderRadius: 8,
          padding: "8px 20px",
          marginBottom: 20,
        }}>
          <span style={{ fontSize: 18, color: BRAND, fontWeight: 700, fontFamily: "system-ui, -apple-system, sans-serif" }}>
            TECH STACK
          </span>
        </div>
        <h1 style={{
          margin: 0,
          fontSize: 52,
          fontWeight: 800,
          color: "#f1f5f9",
          fontFamily: "system-ui, -apple-system, sans-serif",
          textAlign: "center",
        }}>
          Built with production-grade technology
        </h1>
      </div>

      {/* Tech grid */}
      <div style={{
        display: "flex",
        justifyContent: "center",
        flexWrap: "wrap",
        gap: 24,
      }}>
        {techItems.map((item, i) => (
          <TechItem key={i} {...item} />
        ))}
      </div>

      {/* DO highlight at bottom */}
      <div style={{
        marginTop: 48,
        textAlign: "center",
        opacity: interpolate(frame - fps * 1.6, [0, 20], [0, 1], { extrapolateRight: "clamp", extrapolateLeft: "clamp" }),
      }}>
        <p style={{
          margin: 0,
          fontSize: 20,
          color: "#64748b",
          fontFamily: "system-ui, -apple-system, sans-serif",
        }}>
          Deployed on <span style={{ color: "#0080FF", fontWeight: 700 }}>DigitalOcean App Platform</span> with{" "}
          <span style={{ color: BRAND, fontWeight: 700 }}>Gradient AI inference</span> and{" "}
          <span style={{ color: "#6366F1", fontWeight: 700 }}>Managed PostgreSQL</span>
        </p>
      </div>
    </AbsoluteFill>
  );
};
