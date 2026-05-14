import { useEffect, useState } from "react";
import axios from "axios";
import { History, CheckCircle, XCircle } from "lucide-react";

export function EmailLogsDashboard() {
  const [logs, setLogs] = useState<any[]>([]);

  useEffect(() => {
    axios.get("/api/emails/logs").then(res => setLogs(res.data)).catch(console.error);
  }, []);

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h2 className="text-2xl font-bold">Email Logs</h2>
        <div className="text-sm text-gray-500">History of dispatched reports</div>
      </div>

      <div className="bg-white dark:bg-gray-900 rounded-xl border border-gray-200 dark:border-gray-800 shadow-sm overflow-hidden">
        <div className="p-4 border-b border-gray-200 dark:border-gray-800 bg-gray-50 dark:bg-gray-800/50 flex items-center gap-2">
          <History className="w-5 h-5 text-gray-400" />
          <h3 className="font-bold">Dispatch History</h3>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full text-sm text-left">
            <thead className="bg-gray-50 dark:bg-gray-800/50 text-gray-500">
              <tr>
                <th className="px-6 py-3 font-medium">Timestamp</th>
                <th className="px-6 py-3 font-medium">Status</th>
                <th className="px-6 py-3 font-medium">Recipient</th>
                <th className="px-6 py-3 font-medium">Subject</th>
                <th className="px-6 py-3 font-medium">Accounts</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200 dark:divide-gray-800">
              {logs.map((log, i) => (
                <tr key={i} className="hover:bg-gray-50 dark:hover:bg-gray-800/50">
                  <td className="px-6 py-4 text-gray-500 whitespace-nowrap">
                    {new Date(log.timestamp).toLocaleString()}
                  </td>
                  <td className="px-6 py-4">
                    {log.status === "SUCCESS" ? (
                      <span className="flex items-center gap-1 text-green-600 bg-green-50 px-2 py-1 rounded-full text-xs font-bold w-max">
                        <CheckCircle className="w-3 h-3" /> Success
                      </span>
                    ) : (
                      <span className="flex items-center gap-1 text-red-600 bg-red-50 px-2 py-1 rounded-full text-xs font-bold w-max">
                        <XCircle className="w-3 h-3" /> Failed
                      </span>
                    )}
                  </td>
                  <td className="px-6 py-4 font-medium">{log.to}</td>
                  <td className="px-6 py-4 text-gray-600 dark:text-gray-400">{log.subject}</td>
                  <td className="px-6 py-4 text-gray-500">
                    {log.accounts.length} account(s)
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
