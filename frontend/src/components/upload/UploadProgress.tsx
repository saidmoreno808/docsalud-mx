import { CheckCircle, Loader2, XCircle, Clock } from "lucide-react";
import { useProcessingStatus } from "@/hooks/useUpload";
import {
  formatConfidence,
  formatProcessingTime,
  docTypeLabel,
} from "@/utils/formatters";

interface Props {
  documentId: string;
}

interface StepProps {
  label: string;
  done: boolean;
  active: boolean;
  detail?: string;
}

function Step({ label, done, active, detail }: StepProps) {
  return (
    <div className="flex items-center gap-3">
      {done ? (
        <CheckCircle className="h-5 w-5 text-success" />
      ) : active ? (
        <Loader2 className="h-5 w-5 animate-spin text-medical-primary" />
      ) : (
        <Clock className="h-5 w-5 text-slate-300" />
      )}
      <div>
        <p
          className={`text-sm font-medium ${done ? "text-success" : active ? "text-medical-primary" : "text-slate-400"}`}
        >
          {label}
        </p>
        {detail && <p className="text-xs text-slate-500">{detail}</p>}
      </div>
    </div>
  );
}

export default function UploadProgress({ documentId }: Props) {
  const { data: status } = useProcessingStatus(documentId);

  const s = status?.status ?? "pending";
  const isCompleted = s === "completed";
  const isFailed = s === "failed";

  return (
    <div className="card space-y-4">
      <h3 className="text-sm font-semibold text-slate-700">
        Procesando documento
      </h3>

      <div className="space-y-3">
        <Step
          label="Documento recibido"
          done={s !== "pending"}
          active={s === "pending"}
        />
        <Step
          label="OCR en proceso"
          done={isCompleted}
          active={s === "processing"}
          detail={
            status?.ocr_confidence
              ? `Confianza: ${formatConfidence(status.ocr_confidence)}`
              : undefined
          }
        />
        <Step
          label="Clasificacion"
          done={isCompleted && !!status?.document_type}
          active={false}
          detail={
            status?.document_type
              ? `${docTypeLabel(status.document_type)} (${formatConfidence(status.document_type_confidence ?? 0)})`
              : undefined
          }
        />
        {isFailed ? (
          <div className="flex items-center gap-3">
            <XCircle className="h-5 w-5 text-severity-critical" />
            <p className="text-sm font-medium text-severity-critical">
              Error al procesar documento
            </p>
          </div>
        ) : (
          <Step label="Completado" done={isCompleted} active={false} />
        )}
      </div>

      {isCompleted && status?.processing_time_ms && (
        <p className="text-xs text-slate-400">
          Procesado en {formatProcessingTime(status.processing_time_ms)}
        </p>
      )}
    </div>
  );
}
