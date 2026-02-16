interface Props {
  onSelect: (query: string) => void;
}

const SUGGESTIONS = [
  "Cual es el historial del paciente?",
  "Que medicamentos tiene activos?",
  "Ultimos resultados de laboratorio",
  "Hay alertas de riesgo?",
  "Resume las ultimas consultas",
];

export default function QuerySuggestions({ onSelect }: Props) {
  return (
    <div className="flex flex-wrap gap-2">
      {SUGGESTIONS.map((s) => (
        <button
          key={s}
          className="rounded-full bg-slate-100 px-3 py-1.5 text-xs text-slate-600 transition-colors hover:bg-teal-50 hover:text-medical-primary"
          onClick={() => onSelect(s)}
        >
          {s}
        </button>
      ))}
    </div>
  );
}
