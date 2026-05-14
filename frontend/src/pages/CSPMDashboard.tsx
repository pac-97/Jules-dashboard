import { useEffect, useState } from "react";
import axios from "axios";
import { CheckCircle2, XCircle } from "lucide-react";

export function CSPMDashboard() {
  const [cspm, setCspm] = useState<any>(null);

  useEffect(() => {
    axios.get("/api/findings/cspm").then((res) => setCspm(res.data)).catch(console.error);
  }, []);

  if (!cspm) return <div className="p-8 text-center">Loading CSPM Data...</div>;

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h2 className="text-2xl font-bold">CSPM Posture</h2>
        <div className="text-sm text-gray-500">Security Hub & Compliance Benchmarks</div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-white dark:bg-gray-900 p-6 rounded-xl border border-gray-200 dark:border-gray-800 shadow-sm flex flex-col items-center justify-center">
          <div className="text-gray-500 mb-2">Overall Compliance</div>
          <div className="text-4xl font-bold text-primary-500">{cspm.compliance_score}%</div>
        </div>
        <div className="bg-white dark:bg-gray-900 p-6 rounded-xl border border-gray-200 dark:border-gray-800 shadow-sm flex flex-col items-center justify-center">
          <div className="text-gray-500 mb-2">CIS v5.0.0</div>
          <div className="text-4xl font-bold text-green-500">{cspm.cis_score}%</div>
        </div>
        <div className="bg-white dark:bg-gray-900 p-6 rounded-xl border border-gray-200 dark:border-gray-800 shadow-sm flex flex-col items-center justify-center">
          <div className="text-gray-500 mb-2">NIST 800-53 r5</div>
          <div className="text-4xl font-bold text-blue-500">{cspm.nist_score}%</div>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="bg-white dark:bg-gray-900 p-6 rounded-xl border border-gray-200 dark:border-gray-800 shadow-sm">
          <h3 className="font-bold flex items-center gap-2 mb-4">
            <CheckCircle2 className="w-5 h-5 text-green-500" />
            Controls Summary
          </h3>
          <div className="flex justify-between items-center py-2 border-b border-gray-100 dark:border-gray-800">
            <span className="text-gray-500">Passed Controls</span>
            <span className="font-bold text-green-500">{cspm.passed_controls}</span>
          </div>
          <div className="flex justify-between items-center py-2">
            <span className="text-gray-500">Failed Controls</span>
            <span className="font-bold text-red-500">{cspm.failed_controls}</span>
          </div>
        </div>
      </div>

      <div className="bg-white dark:bg-gray-900 rounded-xl border border-gray-200 dark:border-gray-800 shadow-sm overflow-hidden">
        <div className="p-4 border-b border-gray-200 dark:border-gray-800 bg-gray-50 dark:bg-gray-800/50 flex items-center gap-2">
          <XCircle className="w-5 h-5 text-red-500" />
          <h3 className="font-bold">Failed Controls List</h3>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full text-sm text-left">
            <thead className="bg-gray-50 dark:bg-gray-800/50 text-gray-500">
              <tr>
                <th className="px-6 py-3 font-medium">Control ID</th>
                <th className="px-6 py-3 font-medium">Title</th>
                <th className="px-6 py-3 font-medium">Severity</th>
                <th className="px-6 py-3 font-medium">Account ID</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200 dark:divide-gray-800">
              {cspm.findings?.map((f: any, i: number) => (
                <tr key={i} className="hover:bg-gray-50 dark:hover:bg-gray-800/50">
                  <td className="px-6 py-4 font-bold">{f.controlId}</td>
                  <td className="px-6 py-4 text-gray-700 dark:text-gray-300">{f.title}</td>
                  <td className="px-6 py-4">
                    <span className="px-2 py-1 rounded-full text-xs font-bold bg-red-100 text-critical">{f.severity}</span>
                  </td>
                  <td className="px-6 py-4 text-gray-500">{f.accountId}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
