import { Bell, Heart, Menu } from "lucide-react";
import { useQuery } from "@tanstack/react-query";
import * as api from "@/services/api";

interface Props {
  onToggleSidebar: () => void;
}

export default function Header({ onToggleSidebar }: Props) {
  const { data: alerts } = useQuery({
    queryKey: ["alerts", { is_resolved: false }],
    queryFn: () => api.listAlerts({ is_resolved: false }),
    refetchInterval: 30000,
  });

  const alertCount = alerts?.summary.total ?? 0;

  return (
    <header className="sticky top-0 z-30 flex h-16 items-center justify-between border-b border-slate-200 bg-white px-4 lg:px-6">
      <div className="flex items-center gap-3">
        <button
          className="rounded-lg p-2 text-slate-500 hover:bg-slate-100 lg:hidden"
          onClick={onToggleSidebar}
        >
          <Menu className="h-5 w-5" />
        </button>
        <div className="flex items-center gap-2">
          <Heart className="h-6 w-6 text-medical-primary" />
          <span className="text-lg font-bold text-medical-primary">
            DocSalud
          </span>
          <span className="text-lg font-light text-slate-400">MX</span>
        </div>
      </div>

      <div className="flex items-center gap-4">
        <button className="relative rounded-lg p-2 text-slate-500 hover:bg-slate-100">
          <Bell className="h-5 w-5" />
          {alertCount > 0 && (
            <span className="absolute -right-0.5 -top-0.5 flex h-5 w-5 items-center justify-center rounded-full bg-severity-critical text-[10px] font-bold text-white">
              {alertCount > 9 ? "9+" : alertCount}
            </span>
          )}
        </button>
        <div className="flex h-8 w-8 items-center justify-center rounded-full bg-medical-primary text-sm font-medium text-white">
          DS
        </div>
      </div>
    </header>
  );
}
