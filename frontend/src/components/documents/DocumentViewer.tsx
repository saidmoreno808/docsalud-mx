import { Copy, CheckCircle } from "lucide-react";
import { useState } from "react";
import type { Document } from "@/types";
import {
  docTypeLabel,
  formatConfidence,
  formatProcessingTime,
  formatDate,
} from "@/utils/formatters";

interface Props {
  document: Document;
}

export default function DocumentViewer({ document: doc }: Props) {
  const [copied, setCopied] = useState(false);

  async function handleCopy() {
    if (!doc.raw_text) return;
    await navigator.clipboard.writeText(doc.raw_text);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  }

  const confidenceColor =
    (doc.ocr_confidence ?? 0) > 0.8
      ? "bg-green-200"
      : (doc.ocr_confidence ?? 0) > 0.6
        ? "bg-amber-200"
        : "bg-red-200";

  return (
    <div className="card space-y-4">
      <div className="flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-slate-700">
            {docTypeLabel(doc.document_type)}
          </h3>
          <p className="text-xs text-slate-400">
            {doc.original_filename ?? "Sin nombre"} — {formatDate(doc.created_at)}
            {doc.processing_time_ms != null &&
              ` — ${formatProcessingTime(doc.processing_time_ms)}`}
          </p>
        </div>
        {doc.ocr_confidence != null && (
          <div className="text-right">
            <div className="h-2 w-20 rounded-full bg-slate-200">
              <div
                className={`h-2 rounded-full ${confidenceColor}`}
                style={{ width: `${doc.ocr_confidence * 100}%` }}
              />
            </div>
            <p className="mt-1 text-xs text-slate-500">
              OCR: {formatConfidence(doc.ocr_confidence)}
            </p>
          </div>
        )}
      </div>

      {doc.raw_text ? (
        <div className="relative">
          <button
            className="absolute right-2 top-2 rounded-md p-1 text-slate-400 hover:bg-slate-200"
            onClick={handleCopy}
          >
            {copied ? (
              <CheckCircle className="h-4 w-4 text-success" />
            ) : (
              <Copy className="h-4 w-4" />
            )}
          </button>
          <pre className="max-h-96 overflow-auto rounded-lg bg-slate-50 p-4 font-mono text-xs leading-relaxed text-slate-700">
            {doc.raw_text}
          </pre>
        </div>
      ) : (
        <p className="text-sm text-slate-400">Sin texto extraido</p>
      )}
    </div>
  );
}
