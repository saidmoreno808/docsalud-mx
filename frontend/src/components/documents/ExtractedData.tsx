import type { Entity } from "@/types";
import { formatConfidence } from "@/utils/formatters";

interface Props {
  entities: Entity[];
}

const TYPE_COLORS: Record<string, string> = {
  MEDICAMENTO: "bg-blue-50 text-blue-700",
  DOSIS: "bg-blue-50 text-blue-700",
  PRESENTACION: "bg-blue-50 text-blue-700",
  DIAGNOSTICO: "bg-purple-50 text-purple-700",
  CODIGO_CIE10: "bg-purple-50 text-purple-700",
  SIGNO_VITAL: "bg-teal-50 text-teal-700",
  VALOR_MEDICION: "bg-teal-50 text-teal-700",
  RANGO_REFERENCIA: "bg-teal-50 text-teal-700",
  NOMBRE_PACIENTE: "bg-slate-100 text-slate-600",
  NOMBRE_MEDICO: "bg-slate-100 text-slate-600",
  FECHA: "bg-slate-100 text-slate-600",
  INSTITUCION: "bg-slate-100 text-slate-600",
};

function groupByType(entities: Entity[]) {
  const groups: Record<string, Entity[]> = {};
  for (const e of entities) {
    if (!groups[e.entity_type]) groups[e.entity_type] = [];
    groups[e.entity_type].push(e);
  }
  return groups;
}

export default function ExtractedData({ entities }: Props) {
  if (entities.length === 0) {
    return (
      <div className="card py-8 text-center">
        <p className="text-sm text-slate-400">
          No se extrajeron entidades de este documento
        </p>
      </div>
    );
  }

  const groups = groupByType(entities);

  return (
    <div className="card space-y-4">
      <h3 className="text-sm font-semibold text-slate-700">
        Entidades Extraidas ({entities.length})
      </h3>

      {Object.entries(groups).map(([type, items]) => (
        <div key={type}>
          <div className="mb-2 flex items-center gap-2">
            <span className={`badge ${TYPE_COLORS[type] ?? "bg-slate-100 text-slate-600"}`}>
              {type}
            </span>
            <span className="text-xs text-slate-400">({items.length})</span>
          </div>
          <div className="space-y-1">
            {items.map((e) => (
              <div
                key={e.id}
                className="flex items-center justify-between rounded-md border border-slate-100 px-3 py-1.5"
              >
                <div>
                  <span className="text-sm text-slate-700">{e.entity_value}</span>
                  {e.normalized_value && (
                    <span className="ml-2 text-xs text-slate-400">
                      ({e.normalized_value})
                    </span>
                  )}
                </div>
                {e.confidence != null && (
                  <span className="text-xs text-slate-400">
                    {formatConfidence(e.confidence)}
                  </span>
                )}
              </div>
            ))}
          </div>
        </div>
      ))}
    </div>
  );
}
