import { useEffect, useState } from "react";
import axios from "axios";
import { Activity, PlayCircle, Clock } from "lucide-react";

export function OperationsDashboard() {
  const [jobs, setJobs] = useState<any[]>([]);

  useEffect(() => {
    axios.get("/api/operations/jobs").then((res) => setJobs(res.data)).catch(console.error);
  }, []);

  const triggerJob = () => {
    axios.post("/api/operations/trigger-job")
      .then(res => alert(`Job Triggered: ${res.data.job_id}`))
      .catch(console.error);
  };

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h2 className="text-2xl font-bold">Operations & Logs</h2>
        <div className="text-sm text-gray-500">Scheduler & Job History</div>
      </div>

      <div className="bg-white dark:bg-gray-900 rounded-xl border border-gray-200 dark:border-gray-800 shadow-sm overflow-hidden">
        <div className="p-4 border-b border-gray-200 dark:border-gray-800 bg-gray-50 dark:bg-gray-800/50 flex items-center justify-between">
          <h3 className="font-bold flex items-center gap-2">
            <Activity className="w-5 h-5 text-gray-400" />
            Job Execution History
          </h3>
          <button
            onClick={triggerJob}
            className="flex items-center gap-2 bg-primary-600 hover:bg-primary-700 text-white px-4 py-2 rounded-lg text-sm font-medium transition-colors"
          >
            <PlayCircle className="w-4 h-4" />
            Trigger Manual Run
          </button>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full text-sm text-left">
            <thead className="bg-gray-50 dark:bg-gray-800/50 text-gray-500">
              <tr>
                <th className="px-6 py-3 font-medium">Job ID</th>
                <th className="px-6 py-3 font-medium">Type</th>
                <th className="px-6 py-3 font-medium">Status</th>
                <th className="px-6 py-3 font-medium">Started At</th>
                <th className="px-6 py-3 font-medium">Duration</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200 dark:divide-gray-800">
              {jobs.map((job, i) => (
                <tr key={i} className="hover:bg-gray-50 dark:hover:bg-gray-800/50">
                  <td className="px-6 py-4 font-mono text-xs">{job.id}</td>
                  <td className="px-6 py-4 font-medium">{job.type}</td>
                  <td className="px-6 py-4">
                    <span className={`px-2 py-1 rounded-full text-xs font-bold ${
                      job.status === 'SUCCESS' ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'
                    }`}>
                      {job.status}
                    </span>
                  </td>
                  <td className="px-6 py-4 text-gray-500 flex items-center gap-2">
                    <Clock className="w-4 h-4" />
                    {new Date(job.startedAt).toLocaleString()}
                  </td>
                  <td className="px-6 py-4 text-gray-500">{job.duration}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
