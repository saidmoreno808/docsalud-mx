import { AbsoluteFill, interpolate, spring, useCurrentFrame, useVideoConfig } from "remotion";

const BRAND = "#00C4A1";
const ACCENT = "#6366F1";
const BG = "#0a0e1a";

interface FlowNodeProps {
  icon: string;
  title: string;
  subtitle: string;
  color: string;
  delay: number;
  x: number;
  y: number;
}

const FlowNode = ({ icon, title, subtitle, color, delay, x, y }: FlowNodeProps) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const sp = spring({ frame: frame - delay, fps, config: { damping: 14, stiffness: 120 } });
  const opacity = interpolate(frame - delay, [0, 10], [0, 1], { extrapolateRight: "clamp", extrapolateLeft: "clamp" });
  const scale = interpolate(sp, [0, 1], [0.5, 1]);

  return (
    <div style={{
      position: "absolute",
      left: x,
      top: y,
      opacity,
      transform: `scale(${scale})`,
      display: "flex",
      flexDirection: "column",
      alignItems: "center",
      width: 160,
    }}>
      <div style={{
        width: 90,
        height: 90,
        borderRadius: 20,
        background: `linear-gradient(135deg, ${color}30, ${color}10)`,
        border: `2px solid ${color}70`,
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        fontSize: 40,
        marginBottom: 14,
        boxShadow: `0 0 30px ${color}30`,
      }}>
        {icon}
      </div>
      <div style={{
        fontSize: 18,
        fontWeight: 700,
        color: "#f1f5f9",
        fontFamily: "system-ui, -apple-system, sans-serif",
        textAlign: "center",
        marginBottom: 6,
      }}>
        {title}
      </div>
      <div style={{
        fontSize: 14,
        color: "#64748b",
        fontFamily: "system-ui, -apple-system, sans-serif",
        textAlign: "center",
        lineHeight: 1.4,
      }}>
        {subtitle}
      </div>
    </div>
  );
};

interface ArrowProps {
  fromX: number;
  toX: number;
  y: number;
  delay: number;
  color: string;
}

const Arrow = ({ fromX, toX, y, delay, color }: ArrowProps) => {
  const frame = useCurrentFrame();
  const progress = interpolate(frame - delay, [0, 20], [0, 1], { extrapolateRight: "clamp", extrapolateLeft: "clamp" });
  const width = (toX - fromX) * progress;

  return (
    <div style={{
      position: "absolute",
      left: fromX,
      top: y,
      width,
      height: 2,
      background: `linear-gradient(90deg, ${color}, ${color}60)`,
      overflow: "hidden",
    }}>
      {progress > 0.9 && (
        <div style={{
          position: "absolute",
          right: 0,
          top: -5,
          width: 0,
          height: 0,
          borderTop: "6px solid transparent",
          borderBottom: "6px solid transparent",
          borderLeft: `10px solid ${color}`,
        }} />
      )}
    </div>
  );
};

export const SolutionFlowScene = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const titleOpacity = interpolate(frame, [0, 20], [0, 1], { extrapolateRight: "clamp" });
  const titleY = interpolate(frame, [0, 20], [-20, 0], { extrapolateRight: "clamp" });

  const doLabelOpacity = interpolate(frame, [fps * 2.5, fps * 3], [0, 1], { extrapolateRight: "clamp", extrapolateLeft: "clamp" });

  // Node positions (centered in 1920x1080, accounting for 120px padding)
  const baseY = 380;
  const nodeSpacing = 220;
  const startX = 140;

  const nodes = [
    { icon: "📄", title: "Document", subtitle: "PDF / scanned\nimage", color: "#94a3b8", delay: fps * 0.3 },
    { icon: "🔍", title: "OCR", subtitle: "OpenCV +\nTesseract spa", color: "#F59E0B", delay: fps * 0.7 },
    { icon: "🧠", title: "NLP", subtitle: "SpaCy NER\n+ NLTK", color: ACCENT, delay: fps * 1.0 },
    { icon: "📦", title: "RAG", subtitle: "pgvector 384d\n+ Supabase", color: "#8B5CF6", delay: fps * 1.3 },
    { icon: "🤖", title: "DO AI", subtitle: "Llama 3.3 70B\nGradient AI", color: BRAND, delay: fps * 1.6 },
    { icon: "💊", title: "Diagnosis", subtitle: "Structured AI\nanalysis", color: "#10B981", delay: fps * 1.9 },
  ];

  return (
    <AbsoluteFill style={{ background: BG, padding: "80px 120px", display: "flex", flexDirection: "column" }}>
      {/* Title */}
      <div style={{ opacity: titleOpacity, transform: `translateY(${titleY}px)`, marginBottom: 0 }}>
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
            THE SOLUTION
          </span>
        </div>
        <h1 style={{
          margin: 0,
          fontSize: 52,
          fontWeight: 800,
          color: "#f1f5f9",
          fontFamily: "system-ui, -apple-system, sans-serif",
          lineHeight: 1.2,
        }}>
          Complete medical AI pipeline
        </h1>
      </div>

      {/* Flow nodes */}
      <div style={{ position: "relative", flex: 1 }}>
        {nodes.map((node, i) => (
          <FlowNode
            key={i}
            {...node}
            x={startX + i * nodeSpacing - 80}
            y={baseY - 340}
          />
        ))}

        {/* Arrows between nodes */}
        {nodes.slice(0, -1).map((node, i) => (
          <Arrow
            key={i}
            fromX={startX + i * nodeSpacing + 65}
            toX={startX + (i + 1) * nodeSpacing - 80}
            y={baseY - 295}
            delay={node.delay + 8}
            color={nodes[i + 1].color}
          />
        ))}

        {/* DO Gradient AI highlight box */}
        <div style={{
          position: "absolute",
          left: startX + 4 * nodeSpacing - 120,
          top: baseY - 390,
          width: 200,
          height: 200,
          borderRadius: 24,
          border: `2px dashed ${BRAND}60`,
          opacity: doLabelOpacity,
        }} />
        <div style={{
          position: "absolute",
          left: startX + 4 * nodeSpacing - 80,
          top: baseY - 180,
          opacity: doLabelOpacity,
        }}>
          <div style={{
            display: "flex",
            alignItems: "center",
            gap: 8,
            background: `${BRAND}20`,
            border: `1px solid ${BRAND}`,
            borderRadius: 20,
            padding: "6px 14px",
          }}>
            <svg width={18} height={18} viewBox="0 0 18 18">
              <circle cx={9} cy={9} r={9} fill="#0080FF" />
              <text x={9} y={13} textAnchor="middle" fill="white" fontSize={9} fontWeight={900} fontFamily="system-ui">do</text>
            </svg>
            <span style={{ color: BRAND, fontSize: 14, fontWeight: 700, fontFamily: "system-ui, -apple-system, sans-serif" }}>
              Gradient AI
            </span>
          </div>
        </div>
      </div>
    </AbsoluteFill>
  );
};
