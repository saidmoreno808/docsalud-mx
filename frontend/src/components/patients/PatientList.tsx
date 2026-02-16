import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { Users, Search, Plus, ChevronLeft, ChevronRight } from "lucide-react";
import { usePatients, useCreatePatient } from "@/hooks/usePatients";
import { riskScoreColor, riskScoreLabel } from "@/utils/formatters";
import LoadingSpinner from "@/components/common/LoadingSpinner";
import type { PatientCreate } from "@/types";

export default function PatientList() {
  const [page, setPage] = useState(1);
  const [search, setSearch] = useState("");
  const [showForm, setShowForm] = useState(false);
  const navigate = useNavigate();

  const { data, isLoading } = usePatients({ page, page_size: 15, search: search || undefined });
  const createPatient = useCreatePatient();

  function handleCreate(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault();
    const fd = new FormData(e.currentTarget);
    const body: PatientCreate = {
      first_name: fd.get("first_name") as string,
      last_name: fd.get("last_name") as string,
      external_id: (fd.get("external_id") as string) || undefined,
      gender: (fd.get("gender") as string) || undefined,
      blood_type: (fd.get("blood_type") as string) || undefined,
    };
    createPatient.mutate(body, {
      onSuccess: () => setShowForm(false),
    });
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h1 className="text-xl font-bold text-slate-800">Pacientes</h1>
        <button className="btn-primary" onClick={() => setShowForm(!showForm)}>
          <Plus className="h-4 w-4" />
          Registrar
        </button>
      </div>

      {showForm && (
        <form onSubmit={handleCreate} className="card grid grid-cols-2 gap-4">
          <input name="first_name" placeholder="Nombre *" required className="rounded-lg border border-slate-300 px-3 py-2 text-sm" />
          <input name="last_name" placeholder="Apellidos *" required className="rounded-lg border border-slate-300 px-3 py-2 text-sm" />
          <input name="external_id" placeholder="CURP / ID" className="rounded-lg border border-slate-300 px-3 py-2 text-sm" />
          <select name="gender" className="rounded-lg border border-slate-300 px-3 py-2 text-sm">
            <option value="">Genero</option>
            <option value="M">Masculino</option>
            <option value="F">Femenino</option>
          </select>
          <select name="blood_type" className="rounded-lg border border-slate-300 px-3 py-2 text-sm">
            <option value="">Tipo de sangre</option>
            {["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"].map((t) => (
              <option key={t} value={t}>{t}</option>
            ))}
          </select>
          <div className="flex items-end gap-2">
            <button type="submit" className="btn-primary" disabled={createPatient.isPending}>
              Guardar
            </button>
            <button type="button" className="btn-secondary" onClick={() => setShowForm(false)}>
              Cancelar
            </button>
          </div>
        </form>
      )}

      <div className="relative">
        <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-400" />
        <input
          type="text"
          placeholder="Buscar por nombre o CURP..."
          value={search}
          onChange={(e) => { setSearch(e.target.value); setPage(1); }}
          className="w-full rounded-lg border border-slate-300 py-2 pl-10 pr-4 text-sm"
        />
      </div>

      {isLoading ? (
        <LoadingSpinner message="Cargando pacientes..." />
      ) : !data || data.items.length === 0 ? (
        <div className="card flex flex-col items-center py-16">
          <Users className="h-12 w-12 text-slate-300" />
          <p className="mt-3 text-sm text-slate-500">No hay pacientes registrados</p>
        </div>
      ) : (
        <>
          <div className="overflow-x-auto rounded-xl border border-slate-200 bg-white">
            <table className="w-full text-sm">
              <thead className="border-b border-slate-200 bg-slate-50">
                <tr>
                  <th className="px-4 py-3 text-left font-medium text-slate-600">Nombre</th>
                  <th className="px-4 py-3 text-left font-medium text-slate-600">ID</th>
                  <th className="px-4 py-3 text-left font-medium text-slate-600">Condiciones</th>
                  <th className="px-4 py-3 text-left font-medium text-slate-600">Riesgo</th>
                </tr>
              </thead>
              <tbody>
                {data.items.map((p) => (
                  <tr
                    key={p.id}
                    className="cursor-pointer border-b border-slate-100 hover:bg-slate-50"
                    onClick={() => navigate(`/patients/${p.id}`)}
                  >
                    <td className="px-4 py-3 font-medium text-slate-800">
                      {p.first_name} {p.last_name}
                    </td>
                    <td className="px-4 py-3 text-slate-500">{p.external_id ?? "—"}</td>
                    <td className="px-4 py-3">
                      <div className="flex flex-wrap gap-1">
                        {p.chronic_conditions.length > 0
                          ? p.chronic_conditions.map((c) => (
                              <span key={c} className="badge bg-slate-100 text-slate-600">{c}</span>
                            ))
                          : <span className="text-slate-400">—</span>}
                      </div>
                    </td>
                    <td className="px-4 py-3">
                      <span className={`badge ${riskScoreColor(p.risk_score)}`}>
                        {riskScoreLabel(p.risk_score)}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          <div className="flex items-center justify-between">
            <p className="text-sm text-slate-500">
              {data.total} pacientes — Pagina {data.page} de {data.pages}
            </p>
            <div className="flex gap-2">
              <button className="btn-secondary" disabled={page <= 1} onClick={() => setPage(page - 1)}>
                <ChevronLeft className="h-4 w-4" />
              </button>
              <button className="btn-secondary" disabled={page >= data.pages} onClick={() => setPage(page + 1)}>
                <ChevronRight className="h-4 w-4" />
              </button>
            </div>
          </div>
        </>
      )}
    </div>
  );
}
