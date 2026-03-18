export interface DiagnosticResult {
  id: string;
  patient_id: string;
  risk_score: number;
  risk_level: 'BAJO' | 'MODERADO' | 'ALTO' | 'CRÍTICO';
  anomalies: string[];
  recommendations: string[];
  referred_to: string | null;
  suggested_studies: string[];
  confidence: number;
  sources_used: string[];
  gradient_model_used: string;
  created_at: string;
}
