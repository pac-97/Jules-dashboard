import { useEffect, useState } from "react";
import axios from "axios";
import { FileText, Save, Plus } from "lucide-react";
import toast from "react-hot-toast";

export function TemplatesDashboard() {
  const [templates, setTemplates] = useState<any[]>([]);

  useEffect(() => {
    fetchTemplates();
  }, []);

  const fetchTemplates = () => {
    axios.get("/api/templates").then(res => setTemplates(res.data)).catch(console.error);
  };

  const handleSave = () => {
    axios.post("/api/templates", templates).then(() => {
      toast.success("Templates saved successfully");
      fetchTemplates();
    }).catch(() => toast.error("Failed to save templates"));
  };

  const addTemplate = () => {
    setTemplates([...templates, { id: `temp-${Date.now()}`, name: "New Template", subject: "", body: "" }]);
  };

  const updateTemplate = (index: number, field: string, value: string) => {
    const newTemplates = [...templates];
    newTemplates[index][field] = value;
    setTemplates(newTemplates);
  };

  return (
    <div className="space-y-6 pb-20">
      <div className="flex justify-between items-center">
        <h2 className="text-2xl font-bold">Email Templates</h2>
        <div className="flex gap-2">
          <button onClick={addTemplate} className="flex items-center gap-2 bg-gray-100 dark:bg-gray-800 hover:bg-gray-200 text-gray-700 dark:text-gray-200 px-4 py-2 rounded-lg text-sm font-medium transition-colors">
            <Plus className="w-4 h-4" /> Add Template
          </button>
          <button onClick={handleSave} className="flex items-center gap-2 bg-primary-600 hover:bg-primary-700 text-white px-4 py-2 rounded-lg text-sm font-medium transition-colors">
            <Save className="w-4 h-4" /> Save All
          </button>
        </div>
      </div>

      <div className="space-y-6">
        {templates.map((tpl, i) => (
          <div key={tpl.id} className="bg-white dark:bg-gray-900 rounded-xl border border-gray-200 dark:border-gray-800 shadow-sm overflow-hidden">
            <div className="p-4 border-b border-gray-200 dark:border-gray-800 bg-gray-50 dark:bg-gray-800/50 flex items-center gap-2">
              <FileText className="w-5 h-5 text-gray-400" />
              <input
                className="font-bold bg-transparent border-none outline-none focus:ring-2 focus:ring-primary-500 rounded px-2 w-1/3"
                value={tpl.name}
                onChange={(e) => updateTemplate(i, 'name', e.target.value)}
                placeholder="Template Name"
              />
            </div>
            <div className="p-6 space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Subject Line</label>
                <input
                  type="text"
                  value={tpl.subject}
                  onChange={(e) => updateTemplate(i, 'subject', e.target.value)}
                  className="w-full bg-gray-50 dark:bg-gray-950 border border-gray-300 dark:border-gray-700 rounded-md px-4 py-2 text-sm focus:outline-none focus:border-primary-500 focus:ring-1 focus:ring-primary-500"
                  placeholder="Email Subject"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">HTML Body</label>
                <textarea
                  rows={4}
                  value={tpl.body}
                  onChange={(e) => updateTemplate(i, 'body', e.target.value)}
                  className="w-full bg-gray-50 dark:bg-gray-950 border border-gray-300 dark:border-gray-700 rounded-md px-4 py-2 text-sm focus:outline-none focus:border-primary-500 focus:ring-1 focus:ring-primary-500 font-mono"
                  placeholder="<p>HTML Body Here</p>"
                />
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
