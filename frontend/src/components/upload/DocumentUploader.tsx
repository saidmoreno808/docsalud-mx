import { useState } from "react";
import { useDropzone } from "react-dropzone";
import { Upload, FileText, X } from "lucide-react";
import { useUploadDocument } from "@/hooks/useUpload";
import { usePatients } from "@/hooks/usePatients";
import UploadProgress from "./UploadProgress";
import CameraCapture from "./CameraCapture";

const ACCEPTED = {
  "image/jpeg": [".jpg", ".jpeg"],
  "image/png": [".png"],
  "application/pdf": [".pdf"],
};
const MAX_SIZE = 10 * 1024 * 1024;

export default function DocumentUploader() {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [patientId, setPatientId] = useState<string>("");
  const [documentId, setDocumentId] = useState<string | null>(null);

  const upload = useUploadDocument();
  const { data: patients } = usePatients({ page: 1, page_size: 100 });

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    accept: ACCEPTED,
    maxSize: MAX_SIZE,
    multiple: false,
    onDrop: (files) => {
      if (files[0]) setSelectedFile(files[0]);
    },
  });

  function handleUpload() {
    if (!selectedFile) return;
    upload.mutate(
      { file: selectedFile, patientId: patientId || undefined },
      {
        onSuccess: (data) => {
          setDocumentId(data.document_id);
        },
      },
    );
  }

  function handleReset() {
    setSelectedFile(null);
    setDocumentId(null);
    upload.reset();
  }

  if (documentId) {
    return (
      <div className="mx-auto max-w-2xl">
        <UploadProgress documentId={documentId} />
        <button className="btn-secondary mt-4 w-full" onClick={handleReset}>
          Subir otro documento
        </button>
      </div>
    );
  }

  return (
    <div className="mx-auto max-w-2xl space-y-6">
      <div>
        <h1 className="text-xl font-bold text-slate-800">Subir Documento</h1>
        <p className="text-sm text-slate-500">
          Sube una imagen o PDF de un expediente clinico
        </p>
      </div>

      {!selectedFile ? (
        <div className="space-y-4">
          <div
            {...getRootProps()}
            className={`card flex cursor-pointer flex-col items-center justify-center border-2 border-dashed py-16 transition-colors ${
              isDragActive
                ? "border-medical-primary bg-teal-50"
                : "border-slate-300 hover:border-medical-primary"
            }`}
          >
            <input {...getInputProps()} />
            <Upload className="h-10 w-10 text-slate-400" />
            <p className="mt-3 text-sm font-medium text-slate-600">
              {isDragActive
                ? "Suelta el archivo aqui"
                : "Arrastra un archivo o haz clic para seleccionar"}
            </p>
            <p className="mt-1 text-xs text-slate-400">
              JPG, PNG o PDF — Maximo 10 MB
            </p>
          </div>

          <CameraCapture onCapture={setSelectedFile} />
        </div>
      ) : (
        <div className="card space-y-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <FileText className="h-8 w-8 text-medical-secondary" />
              <div>
                <p className="text-sm font-medium text-slate-700">
                  {selectedFile.name}
                </p>
                <p className="text-xs text-slate-400">
                  {(selectedFile.size / 1024).toFixed(0)} KB
                </p>
              </div>
            </div>
            <button
              className="rounded-lg p-1 text-slate-400 hover:bg-slate-100"
              onClick={() => setSelectedFile(null)}
            >
              <X className="h-5 w-5" />
            </button>
          </div>

          {selectedFile.type.startsWith("image/") && (
            <img
              src={URL.createObjectURL(selectedFile)}
              alt="Preview"
              className="max-h-64 rounded-lg object-contain"
            />
          )}

          <div>
            <label className="mb-1 block text-sm font-medium text-slate-700">
              Paciente (opcional)
            </label>
            <select
              value={patientId}
              onChange={(e) => setPatientId(e.target.value)}
              className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm"
            >
              <option value="">Sin paciente asignado</option>
              {patients?.items.map((p) => (
                <option key={p.id} value={p.id}>
                  {p.first_name} {p.last_name}
                </option>
              ))}
            </select>
          </div>

          <button
            className="btn-primary w-full"
            onClick={handleUpload}
            disabled={upload.isPending}
          >
            {upload.isPending ? "Subiendo..." : "Subir Documento"}
          </button>
        </div>
      )}
    </div>
  );
}
