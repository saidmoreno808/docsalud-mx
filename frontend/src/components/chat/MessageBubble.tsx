import type { ChatMessage } from "@/types";
import { formatConfidence, docTypeLabel } from "@/utils/formatters";

interface Props {
  message: ChatMessage;
}

export default function MessageBubble({ message }: Props) {
  const isUser = message.role === "user";

  return (
    <div className={`flex ${isUser ? "justify-end" : "justify-start"} px-4`}>
      <div
        className={`max-w-[80%] space-y-2 ${
          isUser
            ? "rounded-l-2xl rounded-tr-2xl bg-medical-primary px-4 py-3 text-white"
            : "rounded-r-2xl rounded-tl-2xl border border-slate-200 bg-white px-4 py-3 shadow-sm"
        }`}
      >
        <p className="whitespace-pre-wrap text-sm">{message.content}</p>

        {/* Confidence badge */}
        {!isUser && message.confidence != null && message.confidence > 0 && (
          <span className="badge bg-teal-50 text-medical-primary">
            Confianza: {formatConfidence(message.confidence)}
          </span>
        )}

        {/* Sources */}
        {!isUser && message.sources && message.sources.length > 0 && (
          <div className="border-t border-slate-100 pt-2">
            <p className="text-xs font-medium text-slate-400">Fuentes:</p>
            <div className="mt-1 space-y-1">
              {message.sources.map((src, i) => (
                <div key={i} className="flex items-center gap-2 text-xs text-slate-500">
                  <span className="badge bg-slate-100 text-slate-600">
                    {docTypeLabel(src.document_type)}
                  </span>
                  {src.date && <span>{src.date}</span>}
                  <span className="text-slate-400">
                    ({formatConfidence(src.relevance)})
                  </span>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Timestamp */}
        <p
          className={`text-xs ${isUser ? "text-teal-200" : "text-slate-400"}`}
        >
          {message.timestamp.toLocaleTimeString("es-MX", {
            hour: "2-digit",
            minute: "2-digit",
          })}
        </p>
      </div>
    </div>
  );
}
