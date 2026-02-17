import { useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { ArrowLeft, Trash2, Edit } from "lucide-react";
import { usePatient, useDeletePatient, usePatientDocuments } from "@/hooks/usePatients";
import { useQuery } from "@tanstack/react-query";
import * as api from "@/services/api";
import {
  calculateAge,
  riskScoreLabel,
  riskScoreColor,
  formatDate,
} from "@/utils/formatters";
import LoadingSpinner from "@/components/common/LoadingSpinner";
import ConfirmDialog from "@/components/common/ConfirmDialog";
import PatientTimeline from "./PatientTimeline";
import AlertsPanel from "@/components/dashboard/AlertsPanel";

type Tab = "documentos" | "alertas";

export default function PatientDetail() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [tab, setTab] = useState<Tab>("documentos");
  const [showDelete, setShowDelete] = useState(false);

  const { data: patient, isLoading } = usePatient(id);
  const { data: docs } = usePatientDocuments(id);
  const deleteMutation = useDeletePatient();

  // Fetch alerts for this patient
  useQuery({
    queryKey: ["alerts", { patient_id: id, is_resolved: false }],
    queryFn: () => api.listAlerts({ patient_id: id, is_resolved: false }),
    enabled: !!id && tab === "alertas",
  });

  if (isLoading) return <LoadingSpinner message="Cargando paciente..." />;
  if (!patient) {
    return (
      <div className="flex flex-col items-center py-20">
        <p className="text-slate-500">Paciente no encontrado</p>
        <button className="btn-secondary mt-4" onClick={() => navigate("/patients")}>
          Volver a pacientes
        </button>
      </div>
    );
  }

  const age = patient.date_of_birth ? calculateAge(patient.date_of_birth) : null;

  return (
    <div className="space-y-6">
      <button className="btn-secondary" onClick={() => navigate("/patients")}>
        <ArrowLeft className="h-4 w-4" />
        Volver
      </button>

      {/* Patient card */}
      <div className="card">
        <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
          <div>
            <h1 className="text-xl font-bold text-slate-800">
              {patient.first_name} {patient.last_name}
            </h1>
            <div className="mt-1 flex flex-wrap gap-3 text-sm text-slate-500">
              {patient.external_id && <span>ID: {patient.external_id}</span>}
              {age !== null && <span>{age} anos</span>}
              {patient.gender && <span>{patient.gender === "M" ? "Masculino" : "Femenino"}</span>}
              {patient.blood_type && <span>Sangre: {patient.blood_type}</span>}
              <span>Registro: {formatDate(patient.created_at)}</span>
            </div>
          </div>

          <div className="flex items-center gap-3">
            <div className={`rounded-lg px-4 py-2 text-center ${riskScoreColor(patient.risk_score)}`}>
              <p className="text-xs font-medium">Riesgo</p>
              <p className="text-lg font-bold">{riskScoreLabel(patient.risk_score)}</p>
              <p className="text-xs">{(patient.risk_score * 100).toFixed(0)}%</p>
            </div>
            <div className="flex flex-col gap-1">
              <button className="btn-secondary text-xs" onClick={() => navigate(`/patients/${id}`)}>
                <Edit className="h-3 w-3" />
              </button>
              <button className="rounded-lg border border-red-200 p-2 text-severity-critical hover:bg-red-50" onClick={() => setShowDelete(true)}>
                <Trash2 className="h-3 w-3" />
              </button>
            </div>
          </div>
        </div>

        {patient.chronic_conditions.length > 0 && (
          <div className="mt-4 flex flex-wrap gap-2">
            {patient.chronic_conditions.map((c: string) => (
              <span key={c} className="badge bg-teal-50 text-medical-primary">{c}</span>
            ))}
          </div>
        )}
      </div>

      {/* Tabs */}
      <div className="flex gap-1 rounded-lg bg-slate-100 p-1">
        {(["documentos", "alertas"] as Tab[]).map((t) => (
          <button
            key={t}
            className={`flex-1 rounded-md px-4 py-2 text-sm font-medium transition-colors ${
              tab === t ? "bg-white text-medical-primary shadow-sm" : "text-slate-500 hover:text-slate-700"
            }`}
            onClick={() => setTab(t)}
          >
            {t === "documentos" ? "Documentos" : "Alertas"}
          </button>
        ))}
      </div>

      {tab === "documentos" && (
        <PatientTimeline documents={docs?.items ?? []} />
      )}

      {tab === "alertas" && <AlertsPanel />}

      <ConfirmDialog
        isOpen={showDelete}
        onClose={() => setShowDelete(false)}
        onConfirm={() => {
          deleteMutation.mutate(patient.id, {
            onSuccess: () => navigate("/patients"),
          });
        }}
        title="Eliminar paciente"
        message={`¿Estas seguro de eliminar a ${patient.first_name} ${patient.last_name}? Esta accion no se puede deshacer.`}
        confirmLabel="Eliminar"
        variant="danger"
      />
    </div>
  );
}
