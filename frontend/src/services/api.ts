import axios from "axios";
import toast from "react-hot-toast";
import type {
  Patient,
  PatientCreate,
  PatientUpdate,
  PatientListResponse,
  Document,
  DocumentListResponse,
  Alert,
  AlertListResponse,
  AlertResolveRequest,
  UploadResponse,
  ProcessingStatus,
  QueryRequest,
  QueryResponse,
  ClassifyRequest,
  ClassifyResponse,
  SearchResponse,
  HealthResponse,
} from "@/types";

const api = axios.create({
  baseURL: "/api/v1",
  timeout: 30000,
  headers: { "Content-Type": "application/json" },
});

api.interceptors.response.use(
  (response) => response,
  (error) => {
    const message =
      error.response?.data?.detail ?? error.message ?? "Error de conexion";
    if (error.response?.status !== 404) {
      toast.error(message);
    }
    return Promise.reject(error);
  },
);

// --- Health ---

export async function getHealth(): Promise<HealthResponse> {
  const { data } = await api.get<HealthResponse>("/health");
  return data;
}

// --- Upload ---

export async function uploadDocument(
  file: File,
  patientId?: string,
): Promise<UploadResponse> {
  const formData = new FormData();
  formData.append("file", file);
  const params = patientId ? { patient_id: patientId } : {};
  const { data } = await api.post<UploadResponse>("/upload", formData, {
    headers: { "Content-Type": "multipart/form-data" },
    params,
  });
  return data;
}

export async function getProcessingStatus(
  documentId: string,
): Promise<ProcessingStatus> {
  const { data } = await api.get<ProcessingStatus>(
    `/upload/${documentId}/status`,
  );
  return data;
}

// --- Patients ---

export async function createPatient(
  body: PatientCreate,
): Promise<Patient> {
  const { data } = await api.post<Patient>("/patients", body);
  return data;
}

export async function listPatients(params: {
  page?: number;
  page_size?: number;
  search?: string;
}): Promise<PatientListResponse> {
  const { data } = await api.get<PatientListResponse>("/patients", { params });
  return data;
}

export async function getPatient(id: string): Promise<Patient> {
  const { data } = await api.get<Patient>(`/patients/${id}`);
  return data;
}

export async function updatePatient(
  id: string,
  body: PatientUpdate,
): Promise<Patient> {
  const { data } = await api.patch<Patient>(
    `/patients/${id}`,
    body,
  );
  return data;
}

export async function deletePatient(id: string): Promise<void> {
  await api.delete(`/patients/${id}`);
}

// --- Documents ---

export async function listPatientDocuments(
  patientId: string,
  params: {
    doc_type?: string;
    date_from?: string;
    date_to?: string;
    page?: number;
    page_size?: number;
  },
): Promise<DocumentListResponse> {
  const { data } = await api.get<DocumentListResponse>(
    `/patients/${patientId}/documents`,
    { params },
  );
  return data;
}

export async function getDocument(
  patientId: string,
  documentId: string,
): Promise<Document> {
  const { data } = await api.get<Document>(
    `/patients/${patientId}/documents/${documentId}`,
  );
  return data;
}

// --- Alerts ---

export async function listAlerts(params: {
  patient_id?: string;
  severity?: string;
  is_resolved?: boolean;
}): Promise<AlertListResponse> {
  const { data } = await api.get<AlertListResponse>("/alerts", { params });
  return data;
}

export async function resolveAlert(
  alertId: string,
  body?: AlertResolveRequest,
): Promise<Alert> {
  const { data } = await api.patch<Alert>(
    `/alerts/${alertId}/resolve`,
    body ?? {},
  );
  return data;
}

// --- Search ---

export async function searchDocuments(params: {
  q: string;
  patient_id?: string;
  top_k?: number;
}): Promise<SearchResponse> {
  const { data } = await api.get<SearchResponse>("/search", { params });
  return data;
}

// --- Query (RAG) ---

export async function queryDocuments(
  body: QueryRequest,
): Promise<QueryResponse> {
  const { data } = await api.post<QueryResponse>("/query", body);
  return data;
}

// --- Classify ---

export async function classifyText(
  body: ClassifyRequest,
): Promise<ClassifyResponse> {
  const { data } = await api.post<ClassifyResponse>("/classify", body);
  return data;
}
