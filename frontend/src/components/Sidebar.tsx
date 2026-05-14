import { Link, useLocation } from "react-router-dom";
import { LayoutDashboard, Shield, ShieldAlert, Users, Activity, FileText, History } from "lucide-react";

export function Sidebar() {
  const location = useLocation();

  const navItems = [
    { path: "/", label: "Executive Dashboard", icon: LayoutDashboard },
    { path: "/inspector", label: "Inspector Findings", icon: ShieldAlert },
    { path: "/cspm", label: "CSPM Posture", icon: Shield },
    { path: "/owners", label: "Account Owners", icon: Users },
    { path: "/templates", label: "Email Templates", icon: FileText },
    { path: "/logs", label: "Email Logs", icon: History },
    { path: "/operations", label: "Operations Logs", icon: Activity },
  ];

  return (
    <aside className="w-64 bg-gray-900 text-white flex flex-col h-full border-r border-gray-800">
      <div className="p-6">
        <h1 className="text-xl font-bold flex items-center gap-2">
          <Shield className="w-6 h-6 text-primary-500" />
          <span>AWS Security</span>
        </h1>
      </div>
      <nav className="flex-1 px-4 space-y-2">
        {navItems.map((item) => {
          const Icon = item.icon;
          const isActive = location.pathname === item.path;
          return (
            <Link
              key={item.path}
              to={item.path}
              className={`flex items-center gap-3 px-4 py-3 rounded-lg transition-colors ${
                isActive
                  ? "bg-primary-600 text-white"
                  : "text-gray-400 hover:bg-gray-800 hover:text-white"
              }`}
            >
              <Icon className="w-5 h-5" />
              <span className="font-medium">{item.label}</span>
            </Link>
          );
        })}
      </nav>
      <div className="p-4 border-t border-gray-800 text-xs text-gray-500 text-center">
        Enterprise SOC Platform v1.0
      </div>
    </aside>
  );
}
