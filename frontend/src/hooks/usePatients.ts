import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import toast from "react-hot-toast";
import * as api from "@/services/api";
import type { PatientCreate, PatientUpdate } from "@/types";

export function usePatients(params: {
  page?: number;
  page_size?: number;
  search?: string;
}) {
  return useQuery({
    queryKey: ["patients", params],
    queryFn: () => api.listPatients(params),
    placeholderData: (prev) => prev,
  });
}

export function usePatient(id: string | undefined) {
  return useQuery({
    queryKey: ["patient", id],
    queryFn: () => api.getPatient(id!),
    enabled: !!id,
  });
}

export function useCreatePatient() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data: PatientCreate) => api.createPatient(data),
    onSuccess: () => {
      toast.success("Paciente registrado");
      queryClient.invalidateQueries({ queryKey: ["patients"] });
    },
  });
}

export function useUpdatePatient() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: PatientUpdate }) =>
      api.updatePatient(id, data),
    onSuccess: (_data, variables) => {
      toast.success("Paciente actualizado");
      queryClient.invalidateQueries({ queryKey: ["patients"] });
      queryClient.invalidateQueries({ queryKey: ["patient", variables.id] });
    },
  });
}

export function useDeletePatient() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => api.deletePatient(id),
    onSuccess: () => {
      toast.success("Paciente eliminado");
      queryClient.invalidateQueries({ queryKey: ["patients"] });
    },
  });
}

export function usePatientDocuments(
  patientId: string | undefined,
  params: {
    doc_type?: string;
    date_from?: string;
    date_to?: string;
    page?: number;
    page_size?: number;
  } = {},
) {
  return useQuery({
    queryKey: ["patient-documents", patientId, params],
    queryFn: () => api.listPatientDocuments(patientId!, params),
    enabled: !!patientId,
  });
}
