import { useState, useRef, useEffect } from "react";
import { Send, Trash2 } from "lucide-react";
import { useChatStore, useQueryMutation } from "@/hooks/useChat";
import { usePatients } from "@/hooks/usePatients";
import type { QueryType } from "@/types";
import MessageBubble from "./MessageBubble";
import QuerySuggestions from "./QuerySuggestions";

const QUERY_TYPES: { value: QueryType; label: string }[] = [
  { value: "general", label: "General" },
  { value: "medicamentos", label: "Medicamentos" },
  { value: "laboratorio", label: "Laboratorio" },
  { value: "alertas", label: "Alertas" },
];

export default function ChatInterface() {
  const [input, setInput] = useState("");
  const [queryType, setQueryType] = useState<QueryType>("general");
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const { messages, clearMessages, selectedPatientId, setPatientId } = useChatStore();
  const queryMutation = useQueryMutation();
  const { data: patients } = usePatients({ page: 1, page_size: 100 });

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  function handleSend() {
    const question = input.trim();
    if (!question || queryMutation.isPending) return;
    setInput("");
    queryMutation.mutate({ question, queryType });
  }

  function handleKeyDown(e: React.KeyboardEvent) {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  }

  return (
    <div className="flex h-[calc(100vh-8rem)] flex-col">
      {/* Header */}
      <div className="flex items-center justify-between border-b border-slate-200 pb-3">
        <div>
          <h1 className="text-xl font-bold text-slate-800">Consulta IA</h1>
          <p className="text-xs text-slate-500">
            Haz preguntas sobre expedientes clinicos
          </p>
        </div>
        <div className="flex items-center gap-3">
          <select
            value={selectedPatientId ?? ""}
            onChange={(e) => setPatientId(e.target.value || null)}
            className="rounded-lg border border-slate-300 px-3 py-1.5 text-sm"
          >
            <option value="">Todos los pacientes</option>
            {patients?.items.map((p) => (
              <option key={p.id} value={p.id}>
                {p.first_name} {p.last_name}
              </option>
            ))}
          </select>
          {messages.length > 0 && (
            <button
              className="rounded-lg p-2 text-slate-400 hover:bg-slate-100"
              onClick={clearMessages}
              title="Limpiar conversacion"
            >
              <Trash2 className="h-4 w-4" />
            </button>
          )}
        </div>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto py-4">
        {messages.length === 0 ? (
          <div className="flex h-full flex-col items-center justify-center gap-4">
            <p className="text-sm text-slate-400">
              Inicia una conversacion sobre expedientes clinicos
            </p>
            <QuerySuggestions onSelect={(q) => setInput(q)} />
          </div>
        ) : (
          <div className="space-y-4">
            {messages.map((msg) => (
              <MessageBubble key={msg.id} message={msg} />
            ))}
            {queryMutation.isPending && (
              <div className="flex gap-2 px-4">
                <div className="rounded-2xl bg-white px-4 py-3 shadow-sm">
                  <div className="flex gap-1">
                    <span className="h-2 w-2 animate-bounce rounded-full bg-slate-400" />
                    <span className="h-2 w-2 animate-bounce rounded-full bg-slate-400 [animation-delay:0.1s]" />
                    <span className="h-2 w-2 animate-bounce rounded-full bg-slate-400 [animation-delay:0.2s]" />
                  </div>
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>
        )}
      </div>

      {/* Query type + Suggestions */}
      <div className="border-t border-slate-200 pt-3">
        {messages.length > 0 && (
          <div className="mb-2">
            <QuerySuggestions onSelect={(q) => setInput(q)} />
          </div>
        )}

        <div className="mb-2 flex gap-1">
          {QUERY_TYPES.map((qt) => (
            <button
              key={qt.value}
              className={`rounded-full px-3 py-1 text-xs font-medium transition-colors ${
                queryType === qt.value
                  ? "bg-medical-primary text-white"
                  : "bg-slate-100 text-slate-600 hover:bg-slate-200"
              }`}
              onClick={() => setQueryType(qt.value)}
            >
              {qt.label}
            </button>
          ))}
        </div>

        {/* Input */}
        <div className="flex gap-2">
          <textarea
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Escribe tu consulta..."
            rows={1}
            className="flex-1 resize-none rounded-lg border border-slate-300 px-4 py-2.5 text-sm focus:border-medical-primary focus:outline-none focus:ring-1 focus:ring-medical-primary"
          />
          <button
            className="btn-primary px-4"
            onClick={handleSend}
            disabled={!input.trim() || queryMutation.isPending}
          >
            <Send className="h-4 w-4" />
          </button>
        </div>
      </div>
    </div>
  );
}
