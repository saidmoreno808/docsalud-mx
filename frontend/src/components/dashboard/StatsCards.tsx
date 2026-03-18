import { Users, FileText, AlertTriangle, Activity } from "lucide-react";
import { useQuery } from "@tanstack/react-query";
import * as api from "@/services/api";
import { riskScoreColor, riskScoreLabel } from "@/utils/formatters";

interface StatCardProps {
  icon: React.ReactNode;
  label: string;
  value: string | number;
  subtitle?: string;
  colorClass: string;
}

function StatCard({ icon, label, value, subtitle, colorClass }: StatCardProps) {
  return (
    <div className="card flex items-start gap-4">
      <div className={`rounded-lg p-3 ${colorClass}`}>{icon}</div>
      <div>
        <p className="text-2xl font-bold text-slate-800">{value}</p>
        <p className="text-sm text-slate-500">{label}</p>
        {subtitle && <p className="text-xs text-slate-400">{subtitle}</p>}
      </div>
    </div>
  );
}

export default function StatsCards() {
  const { data: stats } = useQuery({
    queryKey: ["stats"],
    queryFn: () => api.getStats(),
    refetchInterval: 30000,
  });
  const { data: alerts } = useQuery({
    queryKey: ["alerts", { is_resolved: false }],
    queryFn: () => api.listAlerts({ is_resolved: false }),
  });

  const totalPatients = stats?.patients ?? 0;
  const totalDocs = stats?.processed_documents ?? 0;
  const alertCount = alerts?.summary.total ?? 0;
  const criticalCount = alerts?.summary.critical ?? 0;

  const avgRisk = stats?.avg_risk_score ?? 0;
  const riskLabel = riskScoreLabel(avgRisk);
  const riskColor = riskScoreColor(avgRisk);

  return (
    <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
      <StatCard
        icon={<Users className="h-6 w-6 text-medical-primary" />}
        label="Registered Patients"
        value={totalPatients}
        colorClass="bg-teal-50"
      />
      <StatCard
        icon={<FileText className="h-6 w-6 text-medical-secondary" />}
        label="Processed Documents"
        value={totalDocs}
        subtitle={totalDocs === 0 ? "No data yet" : undefined}
        colorClass="bg-blue-50"
      />
      <StatCard
        icon={<AlertTriangle className="h-6 w-6 text-severity-medium" />}
        label="Active Alerts"
        value={alertCount}
        subtitle={criticalCount > 0 ? `${criticalCount} critical` : undefined}
        colorClass="bg-amber-50"
      />
      <StatCard
        icon={<Activity className="h-6 w-6 text-severity-high" />}
        label="Average Risk"
        value={riskLabel}
        subtitle={`Score: ${avgRisk.toFixed(2)}`}
        colorClass={riskColor}
      />
    </div>
  );
}
