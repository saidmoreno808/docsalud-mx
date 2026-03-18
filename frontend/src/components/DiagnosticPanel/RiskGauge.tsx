import { useEffect, useRef } from 'react';
import type { DiagnosticResult } from './types';

interface RiskGaugeProps {
  riskScore: number;
  riskLevel: DiagnosticResult['risk_level'];
}

const RADIUS = 72;
const CX = 100;
const CY = 96;
const PATH_LENGTH = Math.PI * RADIUS; // semicircle circumference ≈ 226

function scoreColor(score: number): string {
  if (score < 25) return '#16a34a';  // green-600
  if (score < 50) return '#ca8a04';  // yellow-600
  if (score < 75) return '#ea580c';  // orange-600
  return '#dc2626';                   // red-600
}

function levelLabel(level: DiagnosticResult['risk_level']): string {
  return level;
}

export default function RiskGauge({ riskScore, riskLevel }: RiskGaugeProps) {
  const arcRef = useRef<SVGPathElement>(null);
  const color = scoreColor(riskScore);
  const filled = Math.min(Math.max(riskScore, 0), 100);

  // d attribute: semicircle left→right, bottom center origin
  const d = `M ${CX - RADIUS},${CY} A ${RADIUS},${RADIUS} 0 0 1 ${CX + RADIUS},${CY}`;

  useEffect(() => {
    const el = arcRef.current;
    if (!el) return;
    // Start from 0 then animate to target
    el.style.strokeDashoffset = String(PATH_LENGTH);
    el.style.transition = 'none';
    // Force reflow
    void el.getBoundingClientRect();
    el.style.transition = 'stroke-dashoffset 0.9s cubic-bezier(0.4, 0, 0.2, 1)';
    el.style.strokeDashoffset = String(PATH_LENGTH - (filled / 100) * PATH_LENGTH);
  }, [filled]);

  return (
    <div className="flex flex-col items-center">
      <svg width="200" height="120" viewBox="0 0 200 120" aria-label={`Riesgo ${filled}/100`}>
        {/* Background arc */}
        <path
          d={d}
          fill="none"
          stroke="#e2e8f0"
          strokeWidth="14"
          strokeLinecap="round"
        />
        {/* Colored progress arc */}
        <path
          ref={arcRef}
          d={d}
          fill="none"
          stroke={color}
          strokeWidth="14"
          strokeLinecap="round"
          strokeDasharray={PATH_LENGTH}
          strokeDashoffset={PATH_LENGTH}
        />
        {/* Score number */}
        <text
          x={CX}
          y={CY - 8}
          textAnchor="middle"
          dominantBaseline="middle"
          fontSize="30"
          fontWeight="700"
          fill={color}
        >
          {Math.round(filled)}
        </text>
        {/* Risk level label */}
        <text
          x={CX}
          y={CY + 18}
          textAnchor="middle"
          fontSize="11"
          fontWeight="600"
          fill="#475569"
          letterSpacing="0.05em"
        >
          {levelLabel(riskLevel)}
        </text>
      </svg>
    </div>
  );
}
