import { NavLink } from "react-router-dom";
import {
  LayoutDashboard,
  Upload,
  Users,
  Search,
  MessageCircle,
  X,
} from "lucide-react";

interface Props {
  isOpen: boolean;
  onClose: () => void;
}

const navItems = [
  { to: "/", icon: LayoutDashboard, label: "Dashboard" },
  { to: "/upload", icon: Upload, label: "Subir Documento" },
  { to: "/patients", icon: Users, label: "Pacientes" },
  { to: "/search", icon: Search, label: "Busqueda" },
  { to: "/chat", icon: MessageCircle, label: "Consulta IA" },
];

export default function Sidebar({ isOpen, onClose }: Props) {
  return (
    <>
      {/* Mobile overlay */}
      {isOpen && (
        <div
          className="fixed inset-0 z-40 bg-black/40 lg:hidden"
          onClick={onClose}
        />
      )}

      <aside
        className={`fixed left-0 top-0 z-40 flex h-full w-64 flex-col border-r border-slate-200 bg-white transition-transform lg:translate-x-0 ${
          isOpen ? "translate-x-0" : "-translate-x-full"
        }`}
      >
        {/* Mobile close */}
        <div className="flex items-center justify-between p-4 lg:hidden">
          <span className="font-bold text-medical-primary">Menu</span>
          <button
            className="rounded-lg p-1 text-slate-400 hover:bg-slate-100"
            onClick={onClose}
          >
            <X className="h-5 w-5" />
          </button>
        </div>

        {/* Spacer for header */}
        <div className="hidden h-16 lg:block" />

        <nav className="flex-1 space-y-1 px-3 py-4">
          {navItems.map(({ to, icon: Icon, label }) => (
            <NavLink
              key={to}
              to={to}
              end={to === "/"}
              onClick={onClose}
              className={({ isActive }) =>
                `flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium transition-colors ${
                  isActive
                    ? "border-l-3 border-medical-primary bg-teal-50 text-medical-primary"
                    : "text-slate-600 hover:bg-slate-50 hover:text-slate-900"
                }`
              }
            >
              <Icon className="h-5 w-5" />
              {label}
            </NavLink>
          ))}
        </nav>

        <div className="border-t border-slate-200 p-4">
          <p className="text-xs text-slate-400">DocSalud MX v0.7.0</p>
        </div>
      </aside>
    </>
  );
}
