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
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        setError(null);
        const [summaryRes, trendsRes] = await Promise.all([
          axios.get("/api/dashboard/executive-summary"),
          axios.get("/api/dashboard/trends")
        ]);
        setSummary(summaryRes.data);
        setTrends(trendsRes.data || []);
      } catch (err) {
        console.error("Error fetching dashboard data:", err);
        setError("Failed to load dashboard data. Please try again.");
      }
    };
    
    fetchData();
  }, []);

  if (error) {
    return (
      <div className="p-8 text-center">
        <p className="text-red-600 mb-4">{error}</p>
        <button
          onClick={() => window.location.reload()}
          className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
        >
          Retry
        </button>
      </div>
    );
  }

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
            <div className="text-2xl font-bold">{summary.critical_findings || 0}</div>
          </div>
        </div>

        <div className="bg-white dark:bg-gray-900 p-6 rounded-xl border border-gray-200 dark:border-gray-800 shadow-sm flex items-center gap-4">
          <div className="p-3 bg-orange-100 dark:bg-orange-900/30 text-high rounded-lg">
            <Target className="w-8 h-8" />
          </div>
          <div>
            <div className="text-sm text-gray-500 font-medium">High Findings</div>
            <div className="text-2xl font-bold">{summary.high_findings || 0}</div>
          </div>
        </div>

        <div className="bg-white dark:bg-gray-900 p-6 rounded-xl border border-gray-200 dark:border-gray-800 shadow-sm flex items-center gap-4">
          <div className="p-3 bg-green-100 dark:bg-green-900/30 text-green-600 rounded-lg">
            <ShieldCheck className="w-8 h-8" />
          </div>
          <div>
            <div className="text-sm text-gray-500 font-medium">Compliance Score</div>
            <div className="text-2xl font-bold">{(summary.compliance_score || 0).toFixed(1)}%</div>
          </div>
        </div>

        <div className="bg-white dark:bg-gray-900 p-6 rounded-xl border border-gray-200 dark:border-gray-800 shadow-sm flex items-center gap-4">
          <div className="p-3 bg-blue-100 dark:bg-blue-900/30 text-blue-600 rounded-lg">
            <Activity className="w-8 h-8" />
          </div>
          <div>
            <div className="text-sm text-gray-500 font-medium">Total Findings</div>
            <div className="text-2xl font-bold">{summary.total_findings || 0}</div>
          </div>
        </div>
      </div>

      {trends && trends.length > 0 ? (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <div className="bg-white dark:bg-gray-900 p-6 rounded-xl border border-gray-200 dark:border-gray-800 shadow-sm">
            <h3 className="text-lg font-bold mb-4">Vulnerability Trends (30 Days)</h3>
            <div className="w-full h-72">
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={trends} margin={{ top: 5, right: 30, left: 0, bottom: 5 }}>
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
            <div className="w-full h-72">
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={trends} margin={{ top: 5, right: 30, left: 0, bottom: 5 }}>
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
      ) : (
        <div className="bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-200 dark:border-yellow-800 rounded-xl p-6 text-center">
          <p className="text-yellow-800 dark:text-yellow-200">No trend data available. Historical data will appear here once available.</p>
        </div>
      )}
    </div>
  );
}
