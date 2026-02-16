import { PieChart, Pie, Cell, Tooltip, Legend, ResponsiveContainer } from "recharts";
import { usePatients } from "@/hooks/usePatients";
import type { Patient } from "@/types";

const RISK_LEVELS = [
  { name: "Bajo", min: 0, max: 0.25, color: "#16A34A" },
  { name: "Medio", min: 0.25, max: 0.5, color: "#F59E0B" },
  { name: "Alto", min: 0.5, max: 0.75, color: "#EA580C" },
  { name: "Critico", min: 0.75, max: 1.01, color: "#DC2626" },
];

function groupByRisk(patients: Patient[]) {
  return RISK_LEVELS.map((level) => ({
    name: level.name,
    value: patients.filter(
      (p) => p.risk_score >= level.min && p.risk_score < level.max,
    ).length,
    color: level.color,
  })).filter((d) => d.value > 0);
}

export default function RiskChart() {
  const { data } = usePatients({ page: 1, page_size: 100 });
  const patients = data?.items ?? [];

  if (patients.length === 0) {
    return (
      <div className="card flex flex-col items-center justify-center py-10">
        <p className="text-sm text-slate-500">
          Registre pacientes para ver distribucion de riesgo
        </p>
      </div>
    );
  }

  const chartData = groupByRisk(patients);

  return (
    <div className="card">
      <h3 className="mb-4 text-sm font-semibold text-slate-700">
        Distribucion de Riesgo
      </h3>
      <ResponsiveContainer width="100%" height={250}>
        <PieChart>
          <Pie
            data={chartData}
            cx="50%"
            cy="50%"
            innerRadius={50}
            outerRadius={90}
            dataKey="value"
            label={({ name, value }) => `${name}: ${value}`}
          >
            {chartData.map((entry, i) => (
              <Cell key={i} fill={entry.color} />
            ))}
          </Pie>
          <Tooltip />
          <Legend />
        </PieChart>
      </ResponsiveContainer>
    </div>
  );
}
