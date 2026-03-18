import { AbsoluteFill, interpolate, spring, useCurrentFrame, useVideoConfig, staticFile } from "remotion";

const BRAND = "#00C4A1";
const BG = "#0a0e1a";
const PANEL_BG = "#111827";

export const DemoUploadScene = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  // Title
  const titleOpacity = interpolate(frame, [0, 20], [0, 1], { extrapolateRight: "clamp" });

  // Browser chrome
  const browserSp = spring({ frame: frame - 5, fps, config: { damping: 200 } });
  const browserY = interpolate(browserSp, [0, 1], [80, 0]);
  const browserOpacity = interpolate(frame, [5, 25], [0, 1], { extrapolateRight: "clamp", extrapolateLeft: "clamp" });

  // Upload zone pulse animation
  const pulse = interpolate(Math.sin((frame / fps) * 2 * Math.PI * 0.8), [-1, 1], [0.97, 1.03]);

  // File drag-over effect: appears at 2s
  const dragFrame = frame - fps * 2;
  const dragOpacity = interpolate(dragFrame, [0, 15], [0, 1], { extrapolateRight: "clamp", extrapolateLeft: "clamp" });
  const dragBorder = dragOpacity > 0.1;

  // File item appears at 3s (simulates drop)
  const fileFrame = frame - fps * 3;
  const fileSp = spring({ frame: fileFrame, fps, config: { damping: 18, stiffness: 150 } });
  const fileY = interpolate(fileSp, [0, 1], [-30, 0]);
  const fileOpacity = interpolate(fileFrame, [0, 10], [0, 1], { extrapolateRight: "clamp", extrapolateLeft: "clamp" });

  // Analyze button appears at 4s
  const btnFrame = frame - fps * 4;
  const btnSp = spring({ frame: btnFrame, fps, config: { damping: 200 } });
  const btnScale = interpolate(btnSp, [0, 1], [0.8, 1]);
  const btnOpacity = interpolate(btnFrame, [0, 10], [0, 1], { extrapolateRight: "clamp", extrapolateLeft: "clamp" });

  // Click flash at 5.5s
  const clickFrame = frame - fps * 5.5;
  const clickFlash = interpolate(clickFrame, [0, 8, 12], [0, 1, 0], { extrapolateRight: "clamp", extrapolateLeft: "clamp" });

  // Arrow indicator
  const arrowPulse = interpolate(Math.sin((frame / fps) * 2 * Math.PI), [-1, 1], [0, 8]);

  return (
    <AbsoluteFill style={{ background: BG, padding: "60px 120px", display: "flex", flexDirection: "column" }}>
      {/* Header label */}
      <div style={{ opacity: titleOpacity, marginBottom: 32 }}>
        <div style={{
          display: "inline-flex",
          alignItems: "center",
          gap: 12,
          background: `${BRAND}15`,
          border: `1px solid ${BRAND}40`,
          borderRadius: 8,
          padding: "8px 20px",
          marginBottom: 16,
        }}>
          <span style={{ fontSize: 18, color: BRAND, fontWeight: 700, fontFamily: "system-ui, -apple-system, sans-serif" }}>
            DEMO — STEP 1
          </span>
        </div>
        <h1 style={{
          margin: 0,
          fontSize: 48,
          fontWeight: 800,
          color: "#f1f5f9",
          fontFamily: "system-ui, -apple-system, sans-serif",
        }}>
          Upload your clinical record
        </h1>
      </div>

      {/* Two-column layout */}
      <div style={{ display: "flex", gap: 48, flex: 1, alignItems: "flex-start" }}>
        {/* Browser mockup */}
        <div style={{
          flex: 1.2,
          opacity: browserOpacity,
          transform: `translateY(${browserY}px)`,
          background: PANEL_BG,
          borderRadius: 16,
          border: "1px solid rgba(255,255,255,0.08)",
          overflow: "hidden",
          boxShadow: "0 24px 80px rgba(0,0,0,0.6)",
        }}>
          {/* Browser bar */}
          <div style={{
            display: "flex",
            alignItems: "center",
            gap: 8,
            padding: "12px 20px",
            background: "rgba(255,255,255,0.04)",
            borderBottom: "1px solid rgba(255,255,255,0.06)",
          }}>
            <div style={{ width: 12, height: 12, borderRadius: "50%", background: "#EF4444" }} />
            <div style={{ width: 12, height: 12, borderRadius: "50%", background: "#F59E0B" }} />
            <div style={{ width: 12, height: 12, borderRadius: "50%", background: "#10B981" }} />
            <div style={{
              marginLeft: 16,
              flex: 1,
              background: "rgba(255,255,255,0.06)",
              borderRadius: 6,
              padding: "4px 12px",
              fontSize: 13,
              color: "#64748b",
              fontFamily: "monospace",
            }}>
              clinicaia-docsalud-tk3ds.ondigitalocean.app
            </div>
          </div>

          {/* Upload area */}
          <div style={{ padding: 32 }}>
            {/* Drop zone */}
            <div style={{
              border: `2px dashed ${dragBorder ? BRAND : "rgba(255,255,255,0.15)"}`,
              borderRadius: 16,
              padding: "48px 32px",
              textAlign: "center",
              transform: `scale(${dragBorder ? pulse : 1})`,
              background: dragBorder ? `${BRAND}08` : "transparent",
              transition: "none",
            }}>
              <div style={{ fontSize: 56, marginBottom: 16 }}>📂</div>
              <p style={{
                margin: "0 0 8px",
                fontSize: 20,
                fontWeight: 600,
                color: dragBorder ? BRAND : "#94a3b8",
                fontFamily: "system-ui, -apple-system, sans-serif",
              }}>
                {dragBorder ? "Drop the file here!" : "Drag your record here"}
              </p>
              <p style={{
                margin: 0,
                fontSize: 15,
                color: "#475569",
                fontFamily: "system-ui, -apple-system, sans-serif",
              }}>
                PDF, JPG, PNG — up to 20 MB
              </p>
            </div>

            {/* File item after drop */}
            {fileOpacity > 0.01 && (
              <div style={{
                opacity: fileOpacity,
                transform: `translateY(${fileY}px)`,
                display: "flex",
                alignItems: "center",
                gap: 16,
                marginTop: 20,
                padding: "16px 20px",
                background: "rgba(255,255,255,0.04)",
                border: "1px solid rgba(255,255,255,0.08)",
                borderRadius: 12,
              }}>
                <span style={{ fontSize: 32 }}>📄</span>
                <div style={{ flex: 1 }}>
                  <div style={{
                    fontSize: 16,
                    fontWeight: 600,
                    color: "#e2e8f0",
                    fontFamily: "system-ui, -apple-system, sans-serif",
                    marginBottom: 4,
                  }}>
                    expediente_juan_garcia_2024.pdf
                  </div>
                  <div style={{ fontSize: 13, color: "#64748b", fontFamily: "system-ui, -apple-system, sans-serif" }}>
                    2.4 MB · PDF
                  </div>
                </div>
                <div style={{
                  width: 10, height: 10, borderRadius: "50%",
                  background: BRAND,
                  boxShadow: `0 0 10px ${BRAND}`,
                }} />
              </div>
            )}

            {/* Analyze button */}
            {btnOpacity > 0.01 && (
              <div style={{
                opacity: btnOpacity,
                transform: `scale(${btnScale})`,
                marginTop: 20,
              }}>
                <div style={{
                  background: `linear-gradient(135deg, ${BRAND}, #0EA5E9)`,
                  borderRadius: 12,
                  padding: "16px 32px",
                  textAlign: "center",
                  fontSize: 20,
                  fontWeight: 700,
                  color: "#fff",
                  fontFamily: "system-ui, -apple-system, sans-serif",
                  boxShadow: `0 0 40px ${BRAND}40`,
                  opacity: 1 - clickFlash * 0.3,
                }}>
                  🔬 Analyze Record
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Annotations */}
        <div style={{ flex: 0.8, paddingTop: 40 }}>
          {[
            { icon: "📋", text: "Supports scanned PDFs, prescription photos, and lab reports", delay: fps * 1 },
            { icon: "🌐", text: "Web interface, no installation — access from any device", delay: fps * 1.4 },
            { icon: "🔒", text: "Secure processing — data is not stored permanently", delay: fps * 1.8 },
          ].map((item, i) => {
            const op = interpolate(frame - item.delay, [0, 15], [0, 1], { extrapolateRight: "clamp", extrapolateLeft: "clamp" });
            const tx = interpolate(frame - item.delay, [0, 15], [30, 0], { extrapolateRight: "clamp", extrapolateLeft: "clamp" });
            return (
              <div key={i} style={{
                opacity: op,
                transform: `translateX(${tx}px)`,
                display: "flex",
                gap: 16,
                marginBottom: 28,
                padding: "20px",
                background: "rgba(255,255,255,0.03)",
                border: "1px solid rgba(255,255,255,0.06)",
                borderRadius: 12,
              }}>
                <span style={{ fontSize: 28 }}>{item.icon}</span>
                <p style={{
                  margin: 0,
                  fontSize: 17,
                  color: "#94a3b8",
                  fontFamily: "system-ui, -apple-system, sans-serif",
                  lineHeight: 1.5,
                }}>
                  {item.text}
                </p>
              </div>
            );
          })}

          {/* Arrow pointing to button */}
          {btnOpacity > 0.5 && (
            <div style={{
              display: "flex",
              alignItems: "center",
              gap: 10,
              transform: `translateX(${arrowPulse}px)`,
              marginTop: 16,
            }}>
              <span style={{ fontSize: 32 }}>👆</span>
              <span style={{
                fontSize: 16,
                color: BRAND,
                fontWeight: 600,
                fontFamily: "system-ui, -apple-system, sans-serif",
              }}>
                One click to start the analysis
              </span>
            </div>
          )}
        </div>
      </div>
    </AbsoluteFill>
  );
};
