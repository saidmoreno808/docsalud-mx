import { useState } from "react";
import type { Document } from "@/types";
import DocumentViewer from "./DocumentViewer";
import ExtractedData from "./ExtractedData";

interface Props {
  documents: Document[];
}

export default function DocumentComparison({ documents }: Props) {
  const [leftId, setLeftId] = useState<string>("");
  const [rightId, setRightId] = useState<string>("");

  const leftDoc = documents.find((d) => d.id === leftId);
  const rightDoc = documents.find((d) => d.id === rightId);

  if (documents.length < 2) {
    return (
      <div className="card py-8 text-center">
        <p className="text-sm text-slate-400">
          Se necesitan al menos 2 documentos para comparar
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <div className="rounded-lg bg-amber-50 p-3 text-center text-xs text-amber-700">
        Proximamente: comparacion avanzada con resaltado de diferencias
      </div>

      <div className="grid grid-cols-1 gap-4 lg:grid-cols-2">
        {[
          { selected: leftId, setSelected: setLeftId, doc: leftDoc, label: "Documento A" },
          { selected: rightId, setSelected: setRightId, doc: rightDoc, label: "Documento B" },
        ].map(({ selected, setSelected, doc, label }) => (
          <div key={label} className="space-y-3">
            <select
              value={selected}
              onChange={(e) => setSelected(e.target.value)}
              className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm"
            >
              <option value="">{label}: seleccionar</option>
              {documents.map((d) => (
                <option key={d.id} value={d.id}>
                  {d.original_filename ?? d.document_type} — {d.created_at.slice(0, 10)}
                </option>
              ))}
            </select>
            {doc && (
              <>
                <DocumentViewer document={doc} />
                <ExtractedData entities={doc.entities} />
              </>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
