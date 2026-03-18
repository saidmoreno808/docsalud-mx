import type { DiagnosticResult } from './types';
import RiskGauge from './RiskGauge';

// ── SVG Icons ───────────────────────────────────────────────
function AlertTriangleIcon() {
  return (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="shrink-0 text-amber-500" aria-hidden="true">
      <path d="M10.29 3.86 1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0Z" />
      <line x1="12" y1="9" x2="12" y2="13" />
      <line x1="12" y1="17" x2="12.01" y2="17" />
    </svg>
  );
}

function CheckCircleIcon() {
  return (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="shrink-0 text-teal-600" aria-hidden="true">
      <circle cx="12" cy="12" r="10" />
      <polyline points="9 12 11 14 15 10" />
    </svg>
  );
}

function FlaskIcon() {
  return (
    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="shrink-0 text-blue-500" aria-hidden="true">
      <path d="M9 3h6M9 3v11l-4 6h14l-4-6V3" />
    </svg>
  );
}

// ── Skeleton loader ──────────────────────────────────────────
function DiagnosticSkeleton() {
  return (
    <div className="card animate-pulse space-y-4">
      <div className="flex flex-col items-center gap-2">
        <div className="h-28 w-48 rounded-lg bg-slate-200" />
        <div className="h-3 w-24 rounded bg-slate-200" />
      </div>
      <div className="space-y-2">
        <div className="h-4 w-32 rounded bg-slate-200" />
        <div className="h-3 w-full rounded bg-slate-200" />
        <div className="h-3 w-4/5 rounded bg-slate-200" />
      </div>
      <div className="space-y-2">
        <div className="h-4 w-40 rounded bg-slate-200" />
        <div className="h-3 w-full rounded bg-slate-200" />
        <div className="h-3 w-3/4 rounded bg-slate-200" />
      </div>
    </div>
  );
}

// ── Confidence bar ───────────────────────────────────────────
function ConfidenceBar({ confidence }: { confidence: number }) {
  const pct = Math.round(confidence * 100);
  const color =
    pct >= 80 ? 'bg-teal-500' : pct >= 60 ? 'bg-amber-400' : 'bg-red-400';

  return (
    <div>
      <div className="mb-1 flex justify-between text-xs text-slate-500">
        <span>Confianza del análisis</span>
        <span className="font-semibold text-slate-700">{pct}%</span>
      </div>
      <div className="h-2 w-full overflow-hidden rounded-full bg-slate-200">
        <div
          className={`h-full rounded-full transition-all duration-700 ${color}`}
          style={{ width: `${pct}%` }}
        />
      </div>
    </div>
  );
}

// ── Main component ───────────────────────────────────────────
interface DiagnosticPanelProps {
  result?: DiagnosticResult | null;
  isLoading?: boolean;
  error?: Error | null;
}

export default function DiagnosticPanel({
  result,
  isLoading,
  error,
}: DiagnosticPanelProps) {
  if (isLoading) return <DiagnosticSkeleton />;

  if (error) {
    return (
      <div className="card border border-red-200 bg-red-50">
        <div className="flex items-center gap-3 text-red-700">
          <AlertTriangleIcon />
          <div>
            <p className="font-semibold">Error al analizar el expediente</p>
            <p className="text-sm text-red-500">
              {error.message ?? 'Intenta de nuevo en unos momentos.'}
            </p>
          </div>
        </div>
      </div>
    );
  }

  if (!result) return null;

  return (
    <div className="card space-y-5 border border-blue-100 bg-white shadow-md">
      {/* Header */}
      <div className="flex items-center justify-between">
        <h2 className="text-base font-bold text-slate-800">
          Diagnóstico Predictivo IA
        </h2>
        {result.referred_to && (
          <span className="rounded-full bg-red-100 px-3 py-1 text-xs font-semibold text-red-700">
            Derivar a: {result.referred_to}
          </span>
        )}
      </div>

      {/* Risk gauge */}
      <div className="flex justify-center">
        <RiskGauge riskScore={result.risk_score} riskLevel={result.risk_level} />
      </div>

      {/* Confidence bar */}
      <ConfidenceBar confidence={result.confidence} />

      {/* Hallazgos (anomalies) */}
      {result.anomalies.length > 0 && (
        <section>
          <h3 className="mb-2 text-sm font-semibold uppercase tracking-wide text-amber-600">
            Hallazgos
          </h3>
          <ul className="space-y-1.5">
            {result.anomalies.map((item, i) => (
              <li key={i} className="flex items-start gap-2 text-sm text-slate-700">
                <AlertTriangleIcon />
                <span>{item}</span>
              </li>
            ))}
          </ul>
        </section>
      )}

      {/* Recomendaciones */}
      {result.recommendations.length > 0 && (
        <section>
          <h3 className="mb-2 text-sm font-semibold uppercase tracking-wide text-teal-700">
            Recomendaciones
          </h3>
          <ol className="space-y-1.5">
            {result.recommendations.map((item, i) => (
              <li key={i} className="flex items-start gap-2 text-sm text-slate-700">
                <span className="mt-0.5 flex h-5 w-5 shrink-0 items-center justify-center rounded-full bg-teal-100 text-xs font-bold text-teal-700">
                  {i + 1}
                </span>
                <span>{item}</span>
              </li>
            ))}
          </ol>
        </section>
      )}

      {/* Estudios sugeridos */}
      {result.suggested_studies.length > 0 && (
        <section>
          <h3 className="mb-2 text-sm font-semibold uppercase tracking-wide text-blue-600">
            Estudios sugeridos
          </h3>
          <ul className="space-y-1.5">
            {result.suggested_studies.map((item, i) => (
              <li key={i} className="flex items-center gap-2 text-sm text-slate-700">
                <FlaskIcon />
                <span>{item}</span>
              </li>
            ))}
          </ul>
        </section>
      )}

      {/* Footer */}
      <p className="border-t border-slate-100 pt-3 text-center text-xs text-slate-400">
        Análisis generado por{' '}
        <span className="font-semibold text-blue-500">DO Gradient AI</span>
        {' · '}Modelo:{' '}
        <span className="font-mono">{result.gradient_model_used}</span>
      </p>
    </div>
  );
}
