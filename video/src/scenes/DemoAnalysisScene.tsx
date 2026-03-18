import { AbsoluteFill, interpolate, spring, useCurrentFrame, useVideoConfig } from "remotion";

const BRAND = "#00C4A1";
const ACCENT = "#6366F1";
const BG = "#0a0e1a";
const PANEL_BG = "#111827";

interface StepProps {
  step: number;
  icon: string;
  title: string;
  detail: string;
  color: string;
  delay: number;
  doneAt: number;
}

const AnalysisStep = ({ step, icon, title, detail, color, delay, doneAt }: StepProps) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const opacity = interpolate(frame - delay, [0, 15], [0, 1], { extrapolateRight: "clamp", extrapolateLeft: "clamp" });
  const x = interpolate(frame - delay, [0, 20], [-30, 0], { extrapolateRight: "clamp", extrapolateLeft: "clamp" });

  const isActive = frame >= delay && frame < doneAt;
  const isDone = frame >= doneAt;

  // Progress bar
  const progress = isActive
    ? interpolate(frame, [delay, doneAt], [0, 1], { extrapolateRight: "clamp", extrapolateLeft: "clamp" })
    : isDone ? 1 : 0;

  // Spinner rotation for active step
  const rotation = isActive ? interpolate(frame, [delay, delay + 60], [0, 360], { extrapolateRight: "clamp" }) : 0;

  return (
    <div style={{
      opacity,
      transform: `translateX(${x}px)`,
      display: "flex",
      alignItems: "flex-start",
      gap: 20,
      marginBottom: 28,
      padding: "20px 24px",
      background: isActive ? `${color}10` : "rgba(255,255,255,0.03)",
      border: `1px solid ${isActive ? color + "60" : isDone ? color + "30" : "rgba(255,255,255,0.06)"}`,
      borderRadius: 14,
    }}>
      {/* Status icon */}
      <div style={{
        width: 48,
        height: 48,
        borderRadius: 12,
        background: isDone ? `${color}25` : isActive ? `${color}15` : "rgba(255,255,255,0.04)",
        border: `2px solid ${isDone ? color : isActive ? color + "80" : "rgba(255,255,255,0.1)"}`,
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        fontSize: 22,
        flexShrink: 0,
        transform: isActive ? `rotate(${rotation}deg)` : "none",
      }}>
        {isDone ? "✓" : icon}
      </div>

      <div style={{ flex: 1 }}>
        <div style={{ display: "flex", alignItems: "center", gap: 12, marginBottom: 8 }}>
          <span style={{
            fontSize: 18,
            fontWeight: 700,
            color: isDone ? color : isActive ? "#f1f5f9" : "#64748b",
            fontFamily: "system-ui, -apple-system, sans-serif",
          }}>
            {title}
          </span>
          {isDone && (
            <span style={{
              fontSize: 12,
              background: `${color}20`,
              color,
              borderRadius: 6,
              padding: "2px 8px",
              fontWeight: 600,
              fontFamily: "system-ui, -apple-system, sans-serif",
            }}>
              DONE
            </span>
          )}
          {isActive && (
            <span style={{
              fontSize: 12,
              background: `${color}20`,
              color,
              borderRadius: 6,
              padding: "2px 8px",
              fontWeight: 600,
              fontFamily: "system-ui, -apple-system, sans-serif",
            }}>
              PROCESSING...
            </span>
          )}
        </div>

        <div style={{
          fontSize: 14,
          color: "#64748b",
          fontFamily: "system-ui, -apple-system, sans-serif",
          marginBottom: 10,
        }}>
          {detail}
        </div>

        {/* Progress bar */}
        {(isActive || isDone) && (
          <div style={{
            height: 4,
            background: "rgba(255,255,255,0.08)",
            borderRadius: 2,
            overflow: "hidden",
          }}>
            <div style={{
              height: "100%",
              width: `${progress * 100}%`,
              background: `linear-gradient(90deg, ${color}, ${color}80)`,
              borderRadius: 2,
            }} />
          </div>
        )}
      </div>
    </div>
  );
};

// Animated NER tokens
const NerHighlight = ({ text, label, color, delay }: { text: string; label: string; color: string; delay: number }) => {
  const frame = useCurrentFrame();
  const opacity = interpolate(frame - delay, [0, 12], [0, 1], { extrapolateRight: "clamp", extrapolateLeft: "clamp" });
  const y = interpolate(frame - delay, [0, 12], [10, 0], { extrapolateRight: "clamp", extrapolateLeft: "clamp" });

  return (
    <span style={{
      display: "inline-flex",
      alignItems: "center",
      gap: 4,
      background: `${color}25`,
      border: `1px solid ${color}50`,
      borderRadius: 6,
      padding: "2px 8px",
      margin: "0 4px",
      opacity,
      transform: `translateY(${y}px)`,
    }}>
      <span style={{ color: "#f1f5f9", fontSize: 15, fontFamily: "system-ui, -apple-system, sans-serif" }}>{text}</span>
      <span style={{
        fontSize: 10,
        color,
        fontWeight: 700,
        fontFamily: "monospace",
        background: `${color}30`,
        borderRadius: 4,
        padding: "1px 4px",
      }}>
        {label}
      </span>
    </span>
  );
};

export const DemoAnalysisScene = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const titleOpacity = interpolate(frame, [0, 20], [0, 1], { extrapolateRight: "clamp" });

  const steps: StepProps[] = [
    {
      step: 1,
      icon: "🔍",
      title: "OCR Extraction",
      detail: "OpenCV + Tesseract (spa) — detects text regions and corrects orientation",
      color: "#F59E0B",
      delay: fps * 0.3,
      doneAt: fps * 3,
    },
    {
      step: 2,
      icon: "🧠",
      title: "NLP / NER Analysis",
      detail: "SpaCy es_core_news_sm — labels entities: diagnosis, medications, dates, doctor",
      color: ACCENT,
      delay: fps * 3,
      doneAt: fps * 5.5,
    },
    {
      step: 3,
      icon: "📦",
      title: "Vector indexing",
      detail: "sentence-transformers/all-MiniLM-L6-v2 (384d) → pgvector in Supabase",
      color: "#8B5CF6",
      delay: fps * 5.5,
      doneAt: fps * 7.5,
    },
    {
      step: 4,
      icon: "🤖",
      title: "DO Gradient AI Inference",
      detail: "Llama 3.3 70B via DigitalOcean AI Inference (OpenAI-compatible API)",
      color: BRAND,
      delay: fps * 7.5,
      doneAt: fps * 9.5,
    },
  ];

  const nerOpacity = interpolate(frame, [fps * 5.5, fps * 6], [0, 1], { extrapolateRight: "clamp", extrapolateLeft: "clamp" });

  return (
    <AbsoluteFill style={{ background: BG, padding: "60px 120px", display: "flex", flexDirection: "column" }}>
      {/* Title */}
      <div style={{ opacity: titleOpacity, marginBottom: 32 }}>
        <div style={{
          display: "inline-flex",
          alignItems: "center",
          gap: 12,
          background: `${ACCENT}15`,
          border: `1px solid ${ACCENT}40`,
          borderRadius: 8,
          padding: "8px 20px",
          marginBottom: 16,
        }}>
          <span style={{ fontSize: 18, color: ACCENT, fontWeight: 700, fontFamily: "system-ui, -apple-system, sans-serif" }}>
            DEMO — STEP 2
          </span>
        </div>
        <h1 style={{
          margin: 0,
          fontSize: 48,
          fontWeight: 800,
          color: "#f1f5f9",
          fontFamily: "system-ui, -apple-system, sans-serif",
        }}>
          Real-time analysis pipeline
        </h1>
      </div>

      <div style={{ display: "flex", gap: 48, flex: 1 }}>
        {/* Steps */}
        <div style={{ flex: 1.2 }}>
          {steps.map((step) => (
            <AnalysisStep key={step.step} {...step} />
          ))}
        </div>

        {/* NER visualization panel */}
        <div style={{ flex: 0.9 }}>
          <div style={{
            background: PANEL_BG,
            borderRadius: 16,
            border: "1px solid rgba(255,255,255,0.08)",
            padding: 28,
            opacity: nerOpacity,
          }}>
            <div style={{
              fontSize: 14,
              color: "#64748b",
              fontFamily: "monospace",
              marginBottom: 16,
              textTransform: "uppercase",
              letterSpacing: 1,
            }}>
              Detected entities — NER
            </div>
            <div style={{ lineHeight: 2.2 }}>
              <NerHighlight text="Juan García López" label="PATIENT" color="#10B981" delay={fps * 5.8} />
              {" presents "}
              <NerHighlight text="arterial hypertension" label="DX" color="#EF4444" delay={fps * 6.1} />
              {" grade II. Prescription: "}
              <NerHighlight text="Losartan 50mg" label="MED" color="#3B82F6" delay={fps * 6.4} />
              {" every 24h. Consultation date: "}
              <NerHighlight text="12/03/2025" label="DATE" color="#F59E0B" delay={fps * 6.7} />
              {". Attending physician: "}
              <NerHighlight text="Dr. María Torres" label="DOCTOR" color={ACCENT} delay={fps * 7.0} />
            </div>

            {/* Token stats */}
            <div style={{
              marginTop: 24,
              paddingTop: 20,
              borderTop: "1px solid rgba(255,255,255,0.06)",
              display: "flex",
              gap: 24,
              opacity: interpolate(frame - fps * 7, [0, 15], [0, 1], { extrapolateRight: "clamp", extrapolateLeft: "clamp" }),
            }}>
              {[
                { label: "tokens", value: "847", color: "#94a3b8" },
                { label: "entities", value: "23", color: BRAND },
                { label: "confidence", value: "97%", color: "#10B981" },
              ].map((s) => (
                <div key={s.label} style={{ textAlign: "center" }}>
                  <div style={{ fontSize: 28, fontWeight: 800, color: s.color, fontFamily: "system-ui, -apple-system, sans-serif" }}>
                    {s.value}
                  </div>
                  <div style={{ fontSize: 12, color: "#475569", fontFamily: "system-ui, -apple-system, sans-serif", textTransform: "uppercase", letterSpacing: 0.5 }}>
                    {s.label}
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </AbsoluteFill>
  );
};
