interface Props {
  onSelect: (query: string) => void;
}

const SUGGESTIONS = [
  "What is the patient's history?",
  "What medications are currently active?",
  "Latest laboratory results",
  "Are there any risk alerts?",
  "Summarize the latest consultations",
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
