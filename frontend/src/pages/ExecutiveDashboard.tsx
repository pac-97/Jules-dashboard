import { useEffect, useState } from "react";
import axios from "axios";
import { ShieldAlert, ShieldCheck, Activity, Target } from "lucide-react";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip as RechartsTooltip,
  ResponsiveContainer,
  AreaChart,
  Area
} from "recharts";

export function ExecutiveDashboard() {
  const [summary, setSummary] = useState<any>(null);
  const [trends, setTrends] = useState<any[]>([]);

  useEffect(() => {
    // In a real environment we might configure Axios base URL properly
    axios.get("/api/dashboard/executive-summary").then((res) => setSummary(res.data)).catch(console.error);
    axios.get("/api/dashboard/trends").then((res) => setTrends(res.data)).catch(console.error);
  }, []);

  if (!summary) return <div className="p-8 text-center">Loading Executive Data...</div>;

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h2 className="text-2xl font-bold">Executive Overview</h2>
        <div className="text-sm text-gray-500">Organization-wide Security Posture</div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <div className="bg-white dark:bg-gray-900 p-6 rounded-xl border border-gray-200 dark:border-gray-800 shadow-sm flex items-center gap-4">
          <div className="p-3 bg-red-100 dark:bg-red-900/30 text-critical rounded-lg">
            <ShieldAlert className="w-8 h-8" />
          </div>
          <div>
            <div className="text-sm text-gray-500 font-medium">Critical Findings</div>
            <div className="text-2xl font-bold">{summary.critical_findings}</div>
          </div>
        </div>

        <div className="bg-white dark:bg-gray-900 p-6 rounded-xl border border-gray-200 dark:border-gray-800 shadow-sm flex items-center gap-4">
          <div className="p-3 bg-orange-100 dark:bg-orange-900/30 text-high rounded-lg">
            <Target className="w-8 h-8" />
          </div>
          <div>
            <div className="text-sm text-gray-500 font-medium">High Findings</div>
            <div className="text-2xl font-bold">{summary.high_findings}</div>
          </div>
        </div>

        <div className="bg-white dark:bg-gray-900 p-6 rounded-xl border border-gray-200 dark:border-gray-800 shadow-sm flex items-center gap-4">
          <div className="p-3 bg-green-100 dark:bg-green-900/30 text-green-600 rounded-lg">
            <ShieldCheck className="w-8 h-8" />
          </div>
          <div>
            <div className="text-sm text-gray-500 font-medium">Compliance Score</div>
            <div className="text-2xl font-bold">{summary.compliance_score}%</div>
          </div>
        </div>

        <div className="bg-white dark:bg-gray-900 p-6 rounded-xl border border-gray-200 dark:border-gray-800 shadow-sm flex items-center gap-4">
          <div className="p-3 bg-blue-100 dark:bg-blue-900/30 text-blue-600 rounded-lg">
            <Activity className="w-8 h-8" />
          </div>
          <div>
            <div className="text-sm text-gray-500 font-medium">Total Findings</div>
            <div className="text-2xl font-bold">{summary.total_findings}</div>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white dark:bg-gray-900 p-6 rounded-xl border border-gray-200 dark:border-gray-800 shadow-sm">
          <h3 className="text-lg font-bold mb-4">Vulnerability Trends (30 Days)</h3>
          <div className="h-72">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={trends}>
                <CartesianGrid strokeDasharray="3 3" opacity={0.2} />
                <XAxis dataKey="date" />
                <YAxis />
                <RechartsTooltip />
                <Area type="monotone" dataKey="critical" stackId="1" stroke="#ef4444" fill="#ef4444" opacity={0.8} />
                <Area type="monotone" dataKey="high" stackId="1" stroke="#f97316" fill="#f97316" opacity={0.8} />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>

        <div className="bg-white dark:bg-gray-900 p-6 rounded-xl border border-gray-200 dark:border-gray-800 shadow-sm">
          <h3 className="text-lg font-bold mb-4">Compliance Movement</h3>
          <div className="h-72">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={trends}>
                <CartesianGrid strokeDasharray="3 3" opacity={0.2} />
                <XAxis dataKey="date" />
                <YAxis domain={['auto', 100]} />
                <RechartsTooltip />
                <Line type="monotone" dataKey="compliance_score" stroke="#3b82f6" strokeWidth={3} dot={false} />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>
    </div>
  );
}
