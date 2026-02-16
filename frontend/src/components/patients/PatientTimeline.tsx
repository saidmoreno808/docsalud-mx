import {
  FileText,
  FlaskConical,
  Stethoscope,
  ArrowRightLeft,
  File,
} from "lucide-react";
import { Link } from "react-router-dom";
import type { Document } from "@/types";
import {
  docTypeLabel,
  formatDate,
  formatConfidence,
  statusColor,
  truncate,
} from "@/utils/formatters";

const DOC_ICONS: Record<string, React.ReactNode> = {
  receta: <FileText className="h-4 w-4" />,
  laboratorio: <FlaskConical className="h-4 w-4" />,
  nota_medica: <Stethoscope className="h-4 w-4" />,
  referencia: <ArrowRightLeft className="h-4 w-4" />,
};

interface Props {
  documents: Document[];
}

export default function PatientTimeline({ documents }: Props) {
  if (documents.length === 0) {
    return (
      <div className="card flex flex-col items-center py-10">
        <File className="h-10 w-10 text-slate-300" />
        <p className="mt-3 text-sm text-slate-500">
          No hay documentos para este paciente
        </p>
        <Link to="/upload" className="btn-primary mt-4">
          Subir documento
        </Link>
      </div>
    );
  }

  const sorted = [...documents].sort(
    (a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime(),
  );

  return (
    <div className="relative space-y-4 pl-6">
      <div className="absolute bottom-0 left-2.5 top-0 w-px bg-slate-200" />

      {sorted.map((doc) => (
        <div key={doc.id} className="relative flex gap-4">
          <div className="absolute -left-6 flex h-5 w-5 items-center justify-center rounded-full bg-white text-medical-primary ring-2 ring-slate-200">
            {DOC_ICONS[doc.document_type] ?? <File className="h-3 w-3" />}
          </div>

          <div className="card flex-1 py-3">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <span className="text-sm font-medium text-slate-700">
                  {docTypeLabel(doc.document_type)}
                </span>
                <span className={`badge ${statusColor(doc.processing_status)}`}>
                  {doc.processing_status}
                </span>
              </div>
              <span className="text-xs text-slate-400">
                {formatDate(doc.created_at)}
              </span>
            </div>

            {doc.original_filename && (
              <p className="mt-1 text-xs text-slate-500">
                {doc.original_filename}
              </p>
            )}

            {doc.ocr_confidence != null && (
              <p className="mt-1 text-xs text-slate-400">
                OCR: {formatConfidence(doc.ocr_confidence)}
              </p>
            )}

            {doc.raw_text && (
              <p className="mt-2 rounded bg-slate-50 p-2 font-mono text-xs text-slate-600">
                {truncate(doc.raw_text, 200)}
              </p>
            )}

            {doc.entities.length > 0 && (
              <p className="mt-1 text-xs text-medical-primary">
                {doc.entities.length} entidades extraidas
              </p>
            )}
          </div>
        </div>
      ))}
    </div>
  );
}
