import { AbsoluteFill, interpolate, spring, useCurrentFrame, useVideoConfig } from "remotion";

const BRAND = "#00C4A1";
const ACCENT = "#6366F1";
const BG = "#0a0e1a";
const PANEL_BG = "#111827";
const DANGER = "#EF4444";
const SUCCESS = "#10B981";
const WARNING = "#F59E0B";

interface ConfidenceBarProps {
  label: string;
  value: number;
  color: string;
  delay: number;
}

const ConfidenceBar = ({ label, value, color, delay }: ConfidenceBarProps) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const progress = spring({ frame: frame - delay, fps, config: { damping: 200 } });
  const width = interpolate(progress, [0, 1], [0, value]);
  const opacity = interpolate(frame - delay, [0, 10], [0, 1], { extrapolateRight: "clamp", extrapolateLeft: "clamp" });

  return (
    <div style={{ opacity, marginBottom: 18 }}>
      <div style={{
        display: "flex",
        justifyContent: "space-between",
        marginBottom: 6,
      }}>
        <span style={{ fontSize: 15, color: "#94a3b8", fontFamily: "system-ui, -apple-system, sans-serif" }}>
          {label}
        </span>
        <span style={{ fontSize: 15, fontWeight: 700, color, fontFamily: "system-ui, -apple-system, sans-serif" }}>
          {Math.round(interpolate(progress, [0, 1], [0, value]))}%
        </span>
      </div>
      <div style={{ height: 8, background: "rgba(255,255,255,0.08)", borderRadius: 4 }}>
        <div style={{
          height: "100%",
          width: `${width}%`,
          background: `linear-gradient(90deg, ${color}, ${color}90)`,
          borderRadius: 4,
          boxShadow: `0 0 12px ${color}60`,
        }} />
      </div>
    </div>
  );
};

interface DiagCardProps {
  icon: string;
  label: string;
  value: string;
  sub?: string;
  color: string;
  delay: number;
}

const DiagCard = ({ icon, label, value, sub, color, delay }: DiagCardProps) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const sp = spring({ frame: frame - delay, fps, config: { damping: 14, stiffness: 120 } });
  const opacity = interpolate(frame - delay, [0, 10], [0, 1], { extrapolateRight: "clamp", extrapolateLeft: "clamp" });
  const y = interpolate(sp, [0, 1], [30, 0]);

  return (
    <div style={{
      opacity,
      transform: `translateY(${y}px)`,
      background: `${color}10`,
      border: `1px solid ${color}40`,
      borderRadius: 14,
      padding: "20px 24px",
      flex: 1,
    }}>
      <div style={{ fontSize: 32, marginBottom: 10 }}>{icon}</div>
      <div style={{ fontSize: 13, color: "#64748b", fontFamily: "system-ui, -apple-system, sans-serif", marginBottom: 4, textTransform: "uppercase", letterSpacing: 0.5 }}>
        {label}
      </div>
      <div style={{ fontSize: 18, fontWeight: 700, color: "#f1f5f9", fontFamily: "system-ui, -apple-system, sans-serif", marginBottom: sub ? 4 : 0 }}>
        {value}
      </div>
      {sub && (
        <div style={{ fontSize: 13, color, fontFamily: "system-ui, -apple-system, sans-serif" }}>
          {sub}
        </div>
      )}
    </div>
  );
};

export const DemoResultScene = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const titleOpacity = interpolate(frame, [0, 20], [0, 1], { extrapolateRight: "clamp" });

  const panelSp = spring({ frame: frame - 10, fps, config: { damping: 200 } });
  const panelY = interpolate(panelSp, [0, 1], [60, 0]);
  const panelOpacity = interpolate(frame, [10, 30], [0, 1], { extrapolateRight: "clamp", extrapolateLeft: "clamp" });

  const aiTextDelay = fps * 1.5;
  const aiTextEnd = fps * 3;
  const charCount = Math.round(
    interpolate(frame, [aiTextDelay, aiTextEnd], [0, 280], { extrapolateRight: "clamp", extrapolateLeft: "clamp" })
  );
  const aiText = `58-year-old male patient with confirmed diagnosis of arterial hypertension grade II. Current medication: Losartan 50mg/day. Positive family history for cardiovascular disease. Monitoring every 3 months is recommended and dose adjustment should be evaluated based on treatment response. No relevant drug interactions were identified.`.slice(0, charCount);

  const recDelay = fps * 3.5;

  return (
    <AbsoluteFill style={{ background: BG, padding: "60px 120px", display: "flex", flexDirection: "column" }}>
      {/* Title */}
      <div style={{ opacity: titleOpacity, marginBottom: 28 }}>
        <div style={{
          display: "inline-flex",
          alignItems: "center",
          gap: 12,
          background: `${SUCCESS}15`,
          border: `1px solid ${SUCCESS}40`,
          borderRadius: 8,
          padding: "8px 20px",
          marginBottom: 16,
        }}>
          <span style={{ fontSize: 18, color: SUCCESS, fontWeight: 700, fontFamily: "system-ui, -apple-system, sans-serif" }}>
            DEMO — RESULT
          </span>
        </div>
        <h1 style={{
          margin: 0,
          fontSize: 48,
          fontWeight: 800,
          color: "#f1f5f9",
          fontFamily: "system-ui, -apple-system, sans-serif",
        }}>
          DiagnosticPanel — Structured Medical AI
        </h1>
      </div>

      <div style={{ display: "flex", gap: 40, flex: 1 }}>
        {/* Left: AI analysis */}
        <div style={{
          flex: 1.1,
          opacity: panelOpacity,
          transform: `translateY(${panelY}px)`,
        }}>
          <div style={{
            background: PANEL_BG,
            borderRadius: 16,
            border: "1px solid rgba(255,255,255,0.08)",
            overflow: "hidden",
            height: "100%",
          }}>
            {/* Panel header */}
            <div style={{
              padding: "16px 24px",
              background: "rgba(255,255,255,0.03)",
              borderBottom: "1px solid rgba(255,255,255,0.06)",
              display: "flex",
              alignItems: "center",
              gap: 12,
            }}>
              <div style={{
                width: 10, height: 10, borderRadius: "50%",
                background: BRAND,
                boxShadow: `0 0 10px ${BRAND}`,
              }} />
              <span style={{ fontSize: 15, fontWeight: 600, color: "#94a3b8", fontFamily: "system-ui, -apple-system, sans-serif" }}>
                ClinicaIA · Analysis complete
              </span>
              <div style={{ marginLeft: "auto" }}>
                <span style={{
                  fontSize: 12,
                  background: `${SUCCESS}20`,
                  color: SUCCESS,
                  borderRadius: 6,
                  padding: "3px 10px",
                  fontWeight: 700,
                  fontFamily: "system-ui, -apple-system, sans-serif",
                }}>
                  READY
                </span>
              </div>
            </div>

            <div style={{ padding: 28 }}>
              {/* Summary cards */}
              <div style={{ display: "flex", gap: 16, marginBottom: 28 }}>
                <DiagCard icon="🩺" label="Diagnosis" value="Arterial Hypertension" sub="Grade II — ICD-10: I10" color={DANGER} delay={fps * 0.5} />
                <DiagCard icon="💊" label="Medication" value="Losartan 50mg" sub="1 time per day" color="#3B82F6" delay={fps * 0.8} />
                <DiagCard icon="⚠️" label="Risk" value="MODERATE" sub="Score: 0.62" color={WARNING} delay={fps * 1.1} />
              </div>

              {/* AI text */}
              <div style={{
                background: "rgba(255,255,255,0.03)",
                border: "1px solid rgba(255,255,255,0.06)",
                borderRadius: 12,
                padding: "20px 24px",
                marginBottom: 24,
              }}>
                <div style={{ fontSize: 12, color: "#475569", fontFamily: "monospace", marginBottom: 10, textTransform: "uppercase", letterSpacing: 1 }}>
                  Llama 3.3 70B Analysis — Gradient AI
                </div>
                <p style={{
                  margin: 0,
                  fontSize: 15,
                  color: "#cbd5e1",
                  fontFamily: "system-ui, -apple-system, sans-serif",
                  lineHeight: 1.7,
                  minHeight: 80,
                }}>
                  {aiText}
                  {charCount < 280 && <span style={{ opacity: interpolate(Math.sin(frame * 0.3), [-1, 1], [0, 1]) }}>|</span>}
                </p>
              </div>

              {/* Confidence bars */}
              <div style={{ opacity: interpolate(frame - fps * 2.5, [0, 15], [0, 1], { extrapolateRight: "clamp", extrapolateLeft: "clamp" }) }}>
                <div style={{ fontSize: 12, color: "#475569", fontFamily: "monospace", marginBottom: 14, textTransform: "uppercase", letterSpacing: 1 }}>
                  Confidence by category
                </div>
                <ConfidenceBar label="Primary diagnosis" value={94} color={DANGER} delay={fps * 2.6} />
                <ConfidenceBar label="Medication" value={97} color="#3B82F6" delay={fps * 2.9} />
                <ConfidenceBar label="Follow-up plan" value={88} color={SUCCESS} delay={fps * 3.2} />
              </div>
            </div>
          </div>
        </div>

        {/* Right: Recommendations */}
        <div style={{ flex: 0.75 }}>
          <div style={{
            opacity: interpolate(frame - recDelay, [0, 15], [0, 1], { extrapolateRight: "clamp", extrapolateLeft: "clamp" }),
            marginBottom: 24,
          }}>
            <div style={{
              fontSize: 16,
              fontWeight: 700,
              color: BRAND,
              fontFamily: "system-ui, -apple-system, sans-serif",
              marginBottom: 16,
              textTransform: "uppercase",
              letterSpacing: 0.5,
            }}>
              AI Recommendations
            </div>

            {[
              { text: "Blood pressure check every 3 months", icon: "📅", delay: recDelay },
              { text: "Low-sodium diet (&lt;2g/day) and moderate physical activity", icon: "🥗", delay: recDelay + fps * 0.3 },
              { text: "Biannual renal function evaluation (creatinine, potassium)", icon: "🔬", delay: recDelay + fps * 0.6 },
              { text: "Consider Losartan adjustment if BP &gt;140/90 mmHg", icon: "💊", delay: recDelay + fps * 0.9 },
              { text: "Cardiology referral if risk increases to high", icon: "🏥", delay: recDelay + fps * 1.2 },
            ].map((rec, i) => {
              const op = interpolate(frame - rec.delay, [0, 15], [0, 1], { extrapolateRight: "clamp", extrapolateLeft: "clamp" });
              const tx = interpolate(frame - rec.delay, [0, 15], [20, 0], { extrapolateRight: "clamp", extrapolateLeft: "clamp" });
              return (
                <div key={i} style={{
                  opacity: op,
                  transform: `translateX(${tx}px)`,
                  display: "flex",
                  alignItems: "flex-start",
                  gap: 14,
                  marginBottom: 16,
                  padding: "14px 18px",
                  background: `${BRAND}08`,
                  border: `1px solid ${BRAND}25`,
                  borderRadius: 10,
                }}>
                  <span style={{ fontSize: 22, flexShrink: 0 }}>{rec.icon}</span>
                  <p
                    style={{
                      margin: 0,
                      fontSize: 15,
                      color: "#cbd5e1",
                      fontFamily: "system-ui, -apple-system, sans-serif",
                      lineHeight: 1.5,
                    }}
                    dangerouslySetInnerHTML={{ __html: rec.text }}
                  />
                </div>
              );
            })}
          </div>

          {/* Response time badge */}
          <div style={{
            opacity: interpolate(frame - (recDelay + fps * 1.5), [0, 15], [0, 1], { extrapolateRight: "clamp", extrapolateLeft: "clamp" }),
            display: "flex",
            alignItems: "center",
            gap: 12,
            background: "rgba(255,255,255,0.04)",
            border: "1px solid rgba(255,255,255,0.08)",
            borderRadius: 50,
            padding: "10px 20px",
          }}>
            <span style={{ fontSize: 20 }}>⚡</span>
            <span style={{
              fontSize: 16,
              color: "#94a3b8",
              fontFamily: "system-ui, -apple-system, sans-serif",
            }}>
              Total time: <strong style={{ color: BRAND }}>3.2 seconds</strong>
            </span>
          </div>
        </div>
      </div>
    </AbsoluteFill>
  );
};
