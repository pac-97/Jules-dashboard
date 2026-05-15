import { useEffect, useState } from "react";
import axios from "axios";
import { Cloud, RefreshCw, Send, CheckCircle2, } from "lucide-react";
import toast from "react-hot-toast";

interface Account {
  id: string;
  name: string;
  email: string;
}

interface AccountDetails {
  account_id: string;
  findings_count: number;
  cis_score: number;
  nist_score: number;
  compliance_score: number;
  critical: number;
  high: number;
  medium: number;
  low: number;
}

export function AccountsDashboard() {
  const [accounts, setAccounts] = useState<Account[]>([]);
  const [accountDetails, setAccountDetails] = useState<Record<string, AccountDetails | null>>({});
  const [selectedAccounts, setSelectedAccounts] = useState<Set<string>>(new Set());
  const [loadingAccounts, setLoadingAccounts] = useState<Set<string>>(new Set());
  const [showEmailModal, setShowEmailModal] = useState(false);
  const [emailForm, setEmailForm] = useState({
    to: "",
    cc: "",
    subject: "AWS Security Posture Report",
    body: "Please find attached your consolidated AWS Security findings report."
  });
  const [sending, setSending] = useState(false);

  useEffect(() => {
    loadAccounts();
  }, []);

  const loadAccounts = async () => {
    try {
      const response = await axios.get("/api/operations/accounts");
      setAccounts(response.data || []);
    } catch (error) {
      console.error("Error loading accounts:", error);
      toast.error("Failed to load accounts");
    }
  };

  const fetchAccountDetails = async (accountId: string) => {
    setLoadingAccounts((prev) => new Set([...prev, accountId]));
    try {
      const response = await axios.get(`/api/findings/account-details/${accountId}`);
      setAccountDetails((prev) => ({
        ...prev,
        [accountId]: response.data
      }));
      toast.success(`Loaded findings for account ${accountId}`);
    } catch (error) {
      console.error(`Error fetching details for account ${accountId}:`, error);
      toast.error(`Failed to load findings for account ${accountId}`);
    } finally {
      setLoadingAccounts((prev) => {
        const newSet = new Set(prev);
        newSet.delete(accountId);
        return newSet;
      });
    }
  };

  const toggleAccountSelection = (accountId: string) => {
    const newSelected = new Set(selectedAccounts);
    if (newSelected.has(accountId)) {
      newSelected.delete(accountId);
    } else {
      newSelected.add(accountId);
    }
    setSelectedAccounts(newSelected);
  };

  const handleSendEmail = async () => {
    if (selectedAccounts.size === 0) {
      toast.error("Please select at least one account");
      return;
    }

    if (!emailForm.to) {
      toast.error("Please enter a recipient email");
      return;
    }

    setSending(true);
    try {
      const response = await axios.post("/api/emails/send", {
        to: emailForm.to,
        cc: emailForm.cc,
        subject: emailForm.subject,
        body: emailForm.body,
        accounts: Array.from(selectedAccounts)
      });

      if (response.data.status === "success") {
        toast.success("Email sent successfully!");
        setShowEmailModal(false);
        setEmailForm({
          to: "",
          cc: "",
          subject: "AWS Security Posture Report",
          body: "Please find attached your consolidated AWS Security findings report."
        });
        setSelectedAccounts(new Set());
      }
    } catch (error: any) {
      console.error("Error sending email:", error);
      toast.error(error.response?.data?.detail || "Failed to send email");
    } finally {
      setSending(false);
    }
  };


  if (accounts.length === 0 && loadingAccounts.size === 0) {
    return (
      <div className="p-8 text-center">
        <div className="flex justify-center mb-4">
          <Cloud className="w-12 h-12 text-gray-400" />
        </div>
        <p className="text-gray-500 mb-4">Loading accounts...</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h2 className="text-2xl font-bold">AWS Accounts</h2>
        <div className="flex gap-2">
          <button
            onClick={loadAccounts}
            className="px-4 py-2 bg-gray-200 dark:bg-gray-700 rounded-lg hover:bg-gray-300 dark:hover:bg-gray-600 flex items-center gap-2"
          >
            <RefreshCw className="w-4 h-4" />
            Refresh
          </button>
          {selectedAccounts.size > 0 && (
            <button
              onClick={() => setShowEmailModal(true)}
              className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 flex items-center gap-2"
            >
              <Send className="w-4 h-4" />
              Send Email ({selectedAccounts.size})
            </button>
          )}
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {accounts.map((account) => {
          const details = accountDetails[account.id];
          const isLoading = loadingAccounts.has(account.id);
          const isSelected = selectedAccounts.has(account.id);

          return (
            <div
              key={account.id}
              className={`relative border rounded-xl p-6 transition-all ${
                isSelected
                  ? "bg-blue-50 dark:bg-blue-900/20 border-blue-500 ring-2 ring-blue-300 dark:ring-blue-700"
                  : "bg-white dark:bg-gray-900 border-gray-200 dark:border-gray-800 hover:border-gray-300 dark:hover:border-gray-700"
              }`}
            >
              {/* Selection Checkbox */}
              <div className="absolute top-4 right-4">
                <input
                  type="checkbox"
                  checked={isSelected}
                  onChange={() => toggleAccountSelection(account.id)}
                  className="w-5 h-5 cursor-pointer rounded"
                />
              </div>

              {/* Account Info */}
              <div className="pr-10 mb-4">
                <h3 className="text-lg font-bold text-gray-900 dark:text-white mb-1">
                  {account.name || account.id}
                </h3>
                <p className="text-sm text-gray-500">ID: {account.id}</p>
                {account.email && <p className="text-sm text-gray-500">{account.email}</p>}
              </div>

              {/* Details Section */}
              {details ? (
                <div className="space-y-3 border-t border-gray-200 dark:border-gray-700 pt-4">
                  {/* Findings Count */}
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-gray-600 dark:text-gray-400">Findings</span>
                    <span className="text-lg font-bold text-gray-900 dark:text-white">
                      {details.findings_count}
                    </span>
                  </div>

                  {/* Severity Breakdown */}
                  <div className="grid grid-cols-4 gap-2 text-xs">
                    <div className="text-center p-2 bg-red-50 dark:bg-red-900/20 rounded">
                      <div className="font-bold text-red-600 dark:text-red-400">{details.critical}</div>
                      <div className="text-red-600 dark:text-red-400">Critical</div>
                    </div>
                    <div className="text-center p-2 bg-orange-50 dark:bg-orange-900/20 rounded">
                      <div className="font-bold text-orange-600 dark:text-orange-400">{details.high}</div>
                      <div className="text-orange-600 dark:text-orange-400">High</div>
                    </div>
                    <div className="text-center p-2 bg-yellow-50 dark:bg-yellow-900/20 rounded">
                      <div className="font-bold text-yellow-600 dark:text-yellow-400">{details.medium}</div>
                      <div className="text-yellow-600 dark:text-yellow-400">Med</div>
                    </div>
                    <div className="text-center p-2 bg-blue-50 dark:bg-blue-900/20 rounded">
                      <div className="font-bold text-blue-600 dark:text-blue-400">{details.low}</div>
                      <div className="text-blue-600 dark:text-blue-400">Low</div>
                    </div>
                  </div>

                  {/* Security Scores */}
                  <div className="grid grid-cols-2 gap-2 text-sm">
                    <div>
                      <p className="text-gray-500 text-xs">CIS v5.0.0</p>
                      <p className="text-xl font-bold text-green-600">
                        {details.cis_score.toFixed(1)}%
                      </p>
                    </div>
                    <div>
                      <p className="text-gray-500 text-xs">NIST 800-53</p>
                      <p className="text-xl font-bold text-blue-600">
                        {details.nist_score.toFixed(1)}%
                      </p>
                    </div>
                  </div>
                </div>
              ) : (
                <div className="border-t border-gray-200 dark:border-gray-700 pt-4">
                  <button
                    onClick={() => fetchAccountDetails(account.id)}
                    disabled={isLoading}
                    className="w-full px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-gray-400 flex items-center justify-center gap-2"
                  >
                    {isLoading ? (
                      <>
                        <RefreshCw className="w-4 h-4 animate-spin" />
                        Loading...
                      </>
                    ) : (
                      <>
                        <RefreshCw className="w-4 h-4" />
                        Fetch Findings
                      </>
                    )}
                  </button>
                </div>
              )}
            </div>
          );
        })}
      </div>

      {/* Email Modal */}
      {showEmailModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <div className="bg-white dark:bg-gray-900 rounded-xl shadow-lg max-w-md w-full">
            <div className="p-6 border-b border-gray-200 dark:border-gray-800">
              <h3 className="text-lg font-bold">Send Consolidated Report</h3>
              <p className="text-sm text-gray-500 mt-1">
                Send findings from {selectedAccounts.size} account(s)
              </p>
            </div>

            <div className="p-6 space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                  To Email
                </label>
                <input
                  type="email"
                  value={emailForm.to}
                  onChange={(e) => setEmailForm({ ...emailForm, to: e.target.value })}
                  placeholder="recipient@example.com"
                  className="w-full px-3 py-2 border border-gray-300 dark:border-gray-700 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-white"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                  CC Email (Optional)
                </label>
                <input
                  type="email"
                  value={emailForm.cc}
                  onChange={(e) => setEmailForm({ ...emailForm, cc: e.target.value })}
                  placeholder="cc@example.com"
                  className="w-full px-3 py-2 border border-gray-300 dark:border-gray-700 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-white"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                  Subject
                </label>
                <input
                  type="text"
                  value={emailForm.subject}
                  onChange={(e) => setEmailForm({ ...emailForm, subject: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 dark:border-gray-700 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-white"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                  Message
                </label>
                <textarea
                  value={emailForm.body}
                  onChange={(e) => setEmailForm({ ...emailForm, body: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 dark:border-gray-700 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-white resize-none"
                  rows={4}
                />
              </div>

              <div className="bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg p-3 text-sm text-blue-900 dark:text-blue-200">
                <p className="font-semibold mb-1 flex items-center gap-2">
                  <CheckCircle2 className="w-4 h-4" />
                  Report includes:
                </p>
                <ul className="list-disc list-inside space-y-1 text-xs">
                  <li>CIS AWS Foundations Benchmark v5.0.0 scores and graphs</li>
                  <li>NIST Special Publication 800-53 Revision 5 scores and graphs</li>
                  <li>Consolidated findings from all selected accounts</li>
                </ul>
              </div>
            </div>

            <div className="p-6 border-t border-gray-200 dark:border-gray-800 flex gap-3">
              <button
                onClick={() => setShowEmailModal(false)}
                disabled={sending}
                className="flex-1 px-4 py-2 border border-gray-300 dark:border-gray-700 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-800 disabled:opacity-50"
              >
                Cancel
              </button>
              <button
                onClick={handleSendEmail}
                disabled={sending}
                className="flex-1 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-gray-400 flex items-center justify-center gap-2"
              >
                {sending ? (
                  <>
                    <RefreshCw className="w-4 h-4 animate-spin" />
                    Sending...
                  </>
                ) : (
                  <>
                    <Send className="w-4 h-4" />
                    Send Email
                  </>
                )}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
