import { useDiagnosis } from '@/hooks/useDiagnosis';
import type { DiagnosticResult } from './types';

// SVG: brain / AI spark icon
function AIIcon() {
  return (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
      <path d="M9.5 2A2.5 2.5 0 0 1 12 4.5v15a2.5 2.5 0 0 1-5 0V4.5A2.5 2.5 0 0 1 9.5 2Z" />
      <path d="M14.5 8a2.5 2.5 0 0 1 5 0v8a2.5 2.5 0 0 1-5 0V8Z" />
      <path d="M12 12h2.5" />
      <path d="M9.5 9H7a2 2 0 0 0 0 4h2.5" />
    </svg>
  );
}

interface DiagnosticButtonProps {
  patientId: string;
  onDiagnosed: (result: DiagnosticResult) => void;
}

export default function DiagnosticButton({ patientId, onDiagnosed }: DiagnosticButtonProps) {
  const mutation = useDiagnosis(patientId);

  const handleClick = () => {
    mutation.mutate(undefined, {
      onSuccess: (result) => onDiagnosed(result),
    });
  };

  return (
    <button
      onClick={handleClick}
      disabled={mutation.isPending}
      className={`
        flex items-center gap-2 rounded-lg px-4 py-2 text-sm font-semibold
        transition-all duration-200
        ${mutation.isPending
          ? 'cursor-not-allowed bg-blue-100 text-blue-400'
          : 'bg-blue-700 text-white hover:bg-blue-800 active:scale-95 shadow-sm hover:shadow-md'
        }
      `}
      title="Analyze record with DO Gradient AI"
    >
      {mutation.isPending ? (
        <>
          <svg className="h-4 w-4 animate-spin" viewBox="0 0 24 24" fill="none" aria-hidden="true">
            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v4a4 4 0 00-4 4H4z" />
          </svg>
          Consulting DO Gradient AI...
        </>
      ) : (
        <>
          <AIIcon />
          Analyze with AI
        </>
      )}
    </button>
  );
}
