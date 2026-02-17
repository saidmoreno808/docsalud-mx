// ============================================================
// TypeScript types matching backend Pydantic schemas exactly.
// ============================================================

// --- Patient ---

export interface Patient {
  id: string;
  external_id: string | null;
  first_name: string;
  last_name: string;
  date_of_birth: string | null;
  gender: string | null;
  blood_type: string | null;
  chronic_conditions: string[];
  risk_score: number;
  risk_cluster: number | null;
  created_at: string;
  updated_at: string;
}

export interface PatientCreate {
  external_id?: string | null;
  first_name: string;
  last_name: string;
  date_of_birth?: string | null;
  gender?: string | null;
  blood_type?: string | null;
  chronic_conditions?: string[];
}

export interface PatientUpdate {
  external_id?: string | null;
  first_name?: string | null;
  last_name?: string | null;
  date_of_birth?: string | null;
  gender?: string | null;
  blood_type?: string | null;
  chronic_conditions?: string[] | null;
}

export interface PatientListResponse {
  items: Patient[];
  total: number;
  page: number;
  pages: number;
}

// --- Document ---

export interface Entity {
  id: string;
  entity_type: string;
  entity_value: string;
  normalized_value: string | null;
  confidence: number | null;
  start_char: number | null;
  end_char: number | null;
}

export interface Document {
  id: string;
  patient_id: string | null;
  document_type: string;
  document_type_confidence: number | null;
  original_filename: string | null;
  raw_text: string | null;
  ocr_confidence: number | null;
  extracted_data: Record<string, unknown> | null;
  processing_status: string;
  processing_time_ms: number | null;
  created_at: string;
  entities: Entity[];
}

export interface DocumentListResponse {
  items: Document[];
  total: number;
  page: number;
  pages: number;
}

// --- Alert ---

export interface Alert {
  id: string;
  patient_id: string;
  document_id: string | null;
  alert_type: string;
  severity: string;
  title: string;
  description: string | null;
  is_resolved: boolean;
  resolved_at: string | null;
  created_at: string;
}

export interface AlertSummary {
  total: number;
  critical: number;
  high: number;
  medium: number;
  low: number;
}

export interface AlertListResponse {
  alerts: Alert[];
  summary: AlertSummary;
}

export interface AlertResolveRequest {
  resolution_note?: string | null;
}

// --- Upload ---

export interface UploadResponse {
  document_id: string;
  status: string;
  message: string;
}

export interface ProcessingStatus {
  document_id: string;
  status: string;
  document_type: string | null;
  document_type_confidence: number | null;
  ocr_confidence: number | null;
  processing_time_ms: number | null;
  created_at: string | null;
}

// --- Query / Search / Classify ---

export type QueryType = "general" | "medicamentos" | "laboratorio" | "alertas";

export interface QueryRequest {
  question: string;
  patient_id?: string | null;
  query_type: QueryType;
}

export interface SourceReference {
  document_id: string;
  document_type: string;
  date: string | null;
  relevance: number;
}

export interface QueryResponse {
  answer: string;
  sources: SourceReference[];
  confidence: number;
}

export interface ClassifyRequest {
  text: string;
}

export interface ClassifyResponse {
  document_type: string;
  confidence: number;
  all_probabilities: Record<string, number>;
  model_used: string;
}

export interface SearchResultItem {
  document_id: string;
  chunk_text: string;
  similarity_score: number;
  document_type: string;
  patient_name: string | null;
  date: string | null;
}

export interface SearchResponse {
  results: SearchResultItem[];
}

// --- Health ---

export interface HealthResponse {
  status: string;
  components: Record<string, string>;
  version: string;
  uptime_seconds: number;
}

// --- Chat (frontend-only) ---

export interface ChatMessage {
  id: string;
  role: "user" | "assistant";
  content: string;
  sources?: SourceReference[];
  confidence?: number;
  timestamp: Date;
}
