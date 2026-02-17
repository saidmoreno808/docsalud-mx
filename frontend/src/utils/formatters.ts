import { format, formatDistanceToNow, differenceInYears, parseISO } from "date-fns";
import { es } from "date-fns/locale";

export function formatDate(iso: string): string {
  return format(parseISO(iso), "dd/MM/yyyy");
}

export function formatDateTime(iso: string): string {
  return format(parseISO(iso), "dd/MM/yyyy HH:mm");
}

export function formatRelativeTime(iso: string): string {
  return formatDistanceToNow(parseISO(iso), { addSuffix: true, locale: es });
}

export function calculateAge(dateOfBirth: string): number {
  return differenceInYears(new Date(), parseISO(dateOfBirth));
}

export function riskScoreLabel(score: number): string {
  if (score >= 0.75) return "Critico";
  if (score >= 0.5) return "Alto";
  if (score >= 0.25) return "Medio";
  return "Bajo";
}

export function riskScoreColor(score: number): string {
  if (score >= 0.75) return "text-severity-critical bg-red-50";
  if (score >= 0.5) return "text-severity-high bg-orange-50";
  if (score >= 0.25) return "text-severity-medium bg-amber-50";
  return "text-success bg-green-50";
}

export function severityColor(severity: string): {
  bg: string;
  text: string;
  dot: string;
} {
  const map: Record<string, { bg: string; text: string; dot: string }> = {
    critical: { bg: "bg-red-50", text: "text-severity-critical", dot: "bg-severity-critical" },
    high: { bg: "bg-orange-50", text: "text-severity-high", dot: "bg-severity-high" },
    medium: { bg: "bg-amber-50", text: "text-severity-medium", dot: "bg-severity-medium" },
    low: { bg: "bg-blue-50", text: "text-severity-low", dot: "bg-severity-low" },
  };
  return map[severity] ?? map.low;
}

export function severityLabel(severity: string): string {
  const labels: Record<string, string> = {
    critical: "Critico",
    high: "Alto",
    medium: "Medio",
    low: "Bajo",
  };
  return labels[severity] ?? severity;
}

export function docTypeLabel(docType: string): string {
  const labels: Record<string, string> = {
    receta: "Receta",
    laboratorio: "Laboratorio",
    nota_medica: "Nota Medica",
    referencia: "Referencia",
    consentimiento: "Consentimiento",
    otro: "Otro",
  };
  return labels[docType] ?? docType;
}

export function statusColor(status: string): string {
  const map: Record<string, string> = {
    completed: "bg-green-100 text-green-800",
    processing: "bg-amber-100 text-amber-800",
    pending: "bg-slate-100 text-slate-600",
    failed: "bg-red-100 text-red-800",
  };
  return map[status] ?? map.pending;
}

export function formatConfidence(confidence: number): string {
  return `${(confidence * 100).toFixed(1)}%`;
}

export function formatProcessingTime(ms: number): string {
  if (ms >= 1000) return `${(ms / 1000).toFixed(1)}s`;
  return `${ms}ms`;
}

export function truncate(text: string, maxLen: number): string {
  if (text.length <= maxLen) return text;
  return text.slice(0, maxLen) + "...";
}
