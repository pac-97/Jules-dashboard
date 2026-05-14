import { useEffect, useState } from "react";
import axios from "axios";
import { ShieldAlert } from "lucide-react";

export function InspectorDashboard() {
  const [findings, setFindings] = useState<any[]>([]);

  useEffect(() => {
    axios.get("/api/findings/inspector").then((res) => setFindings(res.data)).catch(console.error);
  }, []);

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h2 className="text-2xl font-bold">Inspector Findings</h2>
        <div className="text-sm text-gray-500">Vulnerability and Network Reachability</div>
      </div>

      <div className="bg-white dark:bg-gray-900 rounded-xl border border-gray-200 dark:border-gray-800 shadow-sm overflow-hidden">
        <div className="p-4 border-b border-gray-200 dark:border-gray-800 bg-gray-50 dark:bg-gray-800/50 flex items-center justify-between">
          <h3 className="font-bold flex items-center gap-2">
            <ShieldAlert className="w-5 h-5 text-gray-400" />
            Global Findings
          </h3>
          <span className="text-xs bg-primary-100 text-primary-800 px-2 py-1 rounded-full">{findings.length} findings</span>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full text-sm text-left">
            <thead className="bg-gray-50 dark:bg-gray-800/50 text-gray-500">
              <tr>
                <th className="px-6 py-3 font-medium">CVE / Title</th>
                <th className="px-6 py-3 font-medium">Severity</th>
                <th className="px-6 py-3 font-medium">Account ID</th>
                <th className="px-6 py-3 font-medium">Resource Type</th>
                <th className="px-6 py-3 font-medium">Region</th>
                <th className="px-6 py-3 font-medium">Status</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200 dark:divide-gray-800">
              {findings.map((f, i) => (
                <tr key={i} className="hover:bg-gray-50 dark:hover:bg-gray-800/50">
                  <td className="px-6 py-4 font-medium">{f.cveId || f.findingType}</td>
                  <td className="px-6 py-4">
                    <span className={`px-2 py-1 rounded-full text-xs font-bold ${
                      f.severity === 'CRITICAL' ? 'bg-red-100 text-critical' :
                      f.severity === 'HIGH' ? 'bg-orange-100 text-high' :
                      f.severity === 'MEDIUM' ? 'bg-yellow-100 text-medium' :
                      'bg-blue-100 text-low'
                    }`}>
                      {f.severity}
                    </span>
                  </td>
                  <td className="px-6 py-4 text-gray-500">{f.accountId}</td>
                  <td className="px-6 py-4 text-gray-500">{f.resourceType}</td>
                  <td className="px-6 py-4 text-gray-500">{f.region}</td>
                  <td className="px-6 py-4 text-gray-500">{f.status}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
