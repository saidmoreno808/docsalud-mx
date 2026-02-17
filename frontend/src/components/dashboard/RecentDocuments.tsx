import { FileText } from "lucide-react";
import { Link } from "react-router-dom";
import type { Document } from "@/types";
import {
  docTypeLabel,
  statusColor,
  formatRelativeTime,
  truncate,
} from "@/utils/formatters";

interface Props {
  documents: Document[];
}

export default function RecentDocuments({ documents }: Props) {
  if (documents.length === 0) {
    return (
      <div className="card flex flex-col items-center justify-center py-10">
        <FileText className="h-10 w-10 text-slate-300" />
        <p className="mt-3 text-sm font-medium text-slate-500">
          No hay documentos procesados
        </p>
        <Link to="/upload" className="btn-primary mt-4">
          Subir primer documento
        </Link>
      </div>
    );
  }

  return (
    <div className="card">
      <div className="mb-4 flex items-center justify-between">
        <h3 className="text-sm font-semibold text-slate-700">
          Documentos Recientes
        </h3>
      </div>
      <div className="space-y-3">
        {documents.slice(0, 5).map((doc) => (
          <div
            key={doc.id}
            className="flex items-center justify-between rounded-lg border border-slate-100 p-3"
          >
            <div className="flex items-center gap-3">
              <FileText className="h-4 w-4 text-slate-400" />
              <div>
                <p className="text-sm font-medium text-slate-700">
                  {truncate(doc.original_filename ?? "Sin nombre", 30)}
                </p>
                <p className="text-xs text-slate-400">
                  {docTypeLabel(doc.document_type)}
                </p>
              </div>
            </div>
            <div className="flex items-center gap-3">
              <span className={`badge ${statusColor(doc.processing_status)}`}>
                {doc.processing_status}
              </span>
              <span className="text-xs text-slate-400">
                {formatRelativeTime(doc.created_at)}
              </span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
