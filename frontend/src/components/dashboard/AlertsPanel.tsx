import { CheckCircle } from "lucide-react";
import { useQuery } from "@tanstack/react-query";
import * as api from "@/services/api";
import {
  severityColor,
  severityLabel,
  formatRelativeTime,
} from "@/utils/formatters";

export default function AlertsPanel() {
  const { data, isLoading } = useQuery({
    queryKey: ["alerts", { is_resolved: false }],
    queryFn: () => api.listAlerts({ is_resolved: false }),
  });

  if (isLoading) {
    return <div className="card animate-pulse h-48" />;
  }

  const alerts = data?.alerts ?? [];
  const summary = data?.summary;

  if (alerts.length === 0) {
    return (
      <div className="card flex flex-col items-center justify-center py-10">
        <CheckCircle className="h-10 w-10 text-success" />
        <p className="mt-3 text-sm font-medium text-slate-500">
          Sin alertas activas
        </p>
      </div>
    );
  }

  return (
    <div className="card">
      <div className="mb-4 flex items-center justify-between">
        <h3 className="text-sm font-semibold text-slate-700">
          Alertas Activas
        </h3>
        {summary && (
          <div className="flex gap-2">
            {summary.critical > 0 && (
              <span className="badge bg-red-100 text-severity-critical">
                {summary.critical} criticas
              </span>
            )}
            {summary.high > 0 && (
              <span className="badge bg-orange-100 text-severity-high">
                {summary.high} altas
              </span>
            )}
          </div>
        )}
      </div>

      <div className="space-y-2">
        {alerts.slice(0, 8).map((alert) => {
          const colors = severityColor(alert.severity);
          return (
            <div
              key={alert.id}
              className={`flex items-center gap-3 rounded-lg p-3 ${colors.bg}`}
            >
              <span className={`h-2.5 w-2.5 rounded-full ${colors.dot}`} />
              <div className="flex-1">
                <p className={`text-sm font-medium ${colors.text}`}>
                  {alert.title}
                </p>
                {alert.description && (
                  <p className="text-xs text-slate-500">{alert.description}</p>
                )}
              </div>
              <div className="text-right">
                <span className="badge bg-white/50 text-xs">
                  {severityLabel(alert.severity)}
                </span>
                <p className="mt-1 text-xs text-slate-400">
                  {formatRelativeTime(alert.created_at)}
                </p>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
