import { useEffect, useState } from "react";
import axios from "axios";
import { Users, Mail, Settings, Send, X } from "lucide-react";
import toast from "react-hot-toast";

export function OwnerDashboard() {
  const [owners, setOwners] = useState<any[]>([]);
  const [templates, setTemplates] = useState<any[]>([]);
  const [selectedOwner, setSelectedOwner] = useState<any>(null);
  const [emailForm, setEmailForm] = useState({ to: '', cc: '', subject: '', body: '', accounts: [] as string[] });

  const fetchOwners = () => axios.get("/api/owners").then(res => setOwners(res.data)).catch(console.error);
  const fetchTemplates = () => axios.get("/api/templates").then(res => setTemplates(res.data)).catch(console.error);

  useEffect(() => {
    fetchOwners();
    fetchTemplates();
  }, []);

  const openSendModal = (owner: any) => {
    setSelectedOwner(owner);
    // Pre-fill with the first template if available, else empty
    const defaultTpl = templates.length > 0 ? templates[0] : { subject: '', body: '' };
    setEmailForm({
      to: owner.email,
      cc: '',
      subject: defaultTpl.subject,
      body: defaultTpl.body,
      accounts: owner.accounts
    });
  };

  const applyTemplate = (templateId: string) => {
    const tpl = templates.find(t => t.id === templateId);
    if (tpl) {
      setEmailForm(prev => ({ ...prev, subject: tpl.subject, body: tpl.body }));
    }
  };

  const handleSendEmail = () => {
    const loadingToast = toast.loading("Generating reports and sending email...");
    axios.post("/api/emails/send", emailForm)
      .then(() => {
        toast.success("Email sent successfully!", { id: loadingToast });
        setSelectedOwner(null);
        fetchOwners();
      })
      .catch(() => {
        toast.error("Failed to send email. Check logs for details.", { id: loadingToast });
      });
  };

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h2 className="text-2xl font-bold">Account Owners</h2>
        <div className="text-sm text-gray-500">Manage Email Consolidation & Mapping</div>
      </div>

      <div className="bg-white dark:bg-gray-900 rounded-xl border border-gray-200 dark:border-gray-800 shadow-sm overflow-hidden">
        <div className="p-4 border-b border-gray-200 dark:border-gray-800 bg-gray-50 dark:bg-gray-800/50 flex items-center justify-between">
          <h3 className="font-bold flex items-center gap-2">
            <Users className="w-5 h-5 text-gray-400" />
            Owner Mappings
          </h3>
          <button
            onClick={() => {
              const tid = toast.loading("Syncing AWS Accounts...");
              axios.post("/api/owners/sync").then(res => {
                toast.success(`Synced ${res.data.synced} new accounts.`, { id: tid });
                fetchOwners();
              }).catch(() => toast.error("Sync failed", { id: tid }));
            }}
            className="bg-primary-600 hover:bg-primary-700 text-white px-4 py-2 rounded-lg text-sm font-medium transition-colors">
            Sync AWS Accounts
          </button>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full text-sm text-left">
            <thead className="bg-gray-50 dark:bg-gray-800/50 text-gray-500">
              <tr>
                <th className="px-6 py-3 font-medium">Owner Email</th>
                <th className="px-6 py-3 font-medium">Owned Accounts</th>
                <th className="px-6 py-3 font-medium">Last Emailed</th>
                <th className="px-6 py-3 font-medium text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200 dark:divide-gray-800">
              {owners.map((owner, i) => (
                <tr key={i} className="hover:bg-gray-50 dark:hover:bg-gray-800/50">
                  <td className="px-6 py-4 font-medium flex items-center gap-2">
                    <Mail className="w-4 h-4 text-gray-400" />
                    {owner.email}
                  </td>
                  <td className="px-6 py-4">
                    <div className="flex flex-wrap gap-1">
                      {owner.accounts.map((acc: string) => (
                        <span key={acc} className="bg-gray-100 dark:bg-gray-800 text-gray-600 dark:text-gray-300 px-2 py-1 rounded text-xs border border-gray-200 dark:border-gray-700">
                          {acc}
                        </span>
                      ))}
                    </div>
                  </td>
                  <td className="px-6 py-4 text-gray-500">{owner.lastEmailed || "Never"}</td>
                  <td className="px-6 py-4 text-right">
                    <div className="flex items-center justify-end gap-2">
                      <button onClick={() => openSendModal(owner)} className="text-gray-500 hover:text-primary-600 flex items-center gap-1 text-xs border border-gray-200 dark:border-gray-700 px-2 py-1 rounded transition-colors bg-white dark:bg-gray-950">
                        <Send className="w-3 h-3" /> Send Report
                      </button>
                      <button className="text-gray-400 hover:text-gray-600 transition-colors">
                        <Settings className="w-5 h-5" />
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {selectedOwner && (
        <div className="fixed inset-0 bg-black/50 z-50 flex items-center justify-center p-4">
          <div className="bg-white dark:bg-gray-900 rounded-xl shadow-xl w-full max-w-2xl overflow-hidden flex flex-col max-h-[90vh]">
            <div className="p-4 border-b border-gray-200 dark:border-gray-800 flex justify-between items-center bg-gray-50 dark:bg-gray-800/50">
              <h3 className="font-bold flex items-center gap-2">
                <Send className="w-5 h-5 text-primary-500" />
                Dispatch Custom Report
              </h3>
              <button onClick={() => setSelectedOwner(null)} className="text-gray-400 hover:text-gray-600">
                <X className="w-5 h-5" />
              </button>
            </div>

            <div className="p-6 overflow-y-auto space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Load Template</label>
                <select
                  onChange={(e) => applyTemplate(e.target.value)}
                  className="w-full bg-gray-50 dark:bg-gray-950 border border-gray-300 dark:border-gray-700 rounded-md px-4 py-2 text-sm focus:outline-none focus:border-primary-500"
                >
                  <option value="">-- Select Template --</option>
                  {templates.map(tpl => (
                    <option key={tpl.id} value={tpl.id}>{tpl.name}</option>
                  ))}
                </select>
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">To</label>
                  <input type="text" value={emailForm.to} onChange={e => setEmailForm({...emailForm, to: e.target.value})} className="w-full bg-gray-50 dark:bg-gray-950 border border-gray-300 dark:border-gray-700 rounded-md px-4 py-2 text-sm focus:outline-none focus:border-primary-500" />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">CC (Comma Separated)</label>
                  <input type="text" value={emailForm.cc} onChange={e => setEmailForm({...emailForm, cc: e.target.value})} className="w-full bg-gray-50 dark:bg-gray-950 border border-gray-300 dark:border-gray-700 rounded-md px-4 py-2 text-sm focus:outline-none focus:border-primary-500" />
                </div>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Subject</label>
                <input type="text" value={emailForm.subject} onChange={e => setEmailForm({...emailForm, subject: e.target.value})} className="w-full bg-gray-50 dark:bg-gray-950 border border-gray-300 dark:border-gray-700 rounded-md px-4 py-2 text-sm focus:outline-none focus:border-primary-500" />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Body (HTML)</label>
                <textarea rows={6} value={emailForm.body} onChange={e => setEmailForm({...emailForm, body: e.target.value})} className="w-full font-mono bg-gray-50 dark:bg-gray-950 border border-gray-300 dark:border-gray-700 rounded-md px-4 py-2 text-sm focus:outline-none focus:border-primary-500" />
              </div>
              <div className="bg-primary-50 dark:bg-primary-900/20 p-3 rounded-lg border border-primary-100 dark:border-primary-800 text-xs text-primary-700 dark:text-primary-300">
                <span className="font-bold">Attachments: </span> Inspector_Report.xlsx, CSPM_Report.xlsx, Accounts_Report.xlsx, Trend_Chart.png
              </div>
            </div>

            <div className="p-4 border-t border-gray-200 dark:border-gray-800 bg-gray-50 dark:bg-gray-800/50 flex justify-end gap-3">
              <button onClick={() => setSelectedOwner(null)} className="px-4 py-2 text-sm font-medium text-gray-600 hover:text-gray-800 transition-colors">Cancel</button>
              <button onClick={handleSendEmail} className="bg-primary-600 hover:bg-primary-700 text-white px-6 py-2 rounded-lg text-sm font-medium transition-colors">
                Confirm & Send
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
