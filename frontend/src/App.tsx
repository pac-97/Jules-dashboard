import { BrowserRouter, Routes, Route } from "react-router-dom";
import { Sidebar } from "./components/Sidebar";
import { Header } from "./components/Header";
import { ExecutiveDashboard } from "./pages/ExecutiveDashboard";
import { InspectorDashboard } from "./pages/InspectorDashboard";
import { CSPMDashboard } from "./pages/CSPMDashboard";
import { OwnerDashboard } from "./pages/OwnerDashboard";
import { OperationsDashboard } from "./pages/OperationsDashboard";
import { TemplatesDashboard } from "./pages/TemplatesDashboard";
import { EmailLogsDashboard } from "./pages/EmailLogsDashboard";
import { Toaster } from "react-hot-toast";

function App() {
  return (
    <BrowserRouter>
      <div className="flex h-screen w-full bg-gray-50 dark:bg-gray-950 overflow-hidden font-sans">
        <Sidebar />
        <div className="flex-1 flex flex-col h-full overflow-hidden">
          <Header />
          <main className="flex-1 overflow-auto p-6">
            <Routes>
              <Route path="/" element={<ExecutiveDashboard />} />
              <Route path="/inspector" element={<InspectorDashboard />} />
              <Route path="/cspm" element={<CSPMDashboard />} />
              <Route path="/owners" element={<OwnerDashboard />} />
              <Route path="/templates" element={<TemplatesDashboard />} />
              <Route path="/logs" element={<EmailLogsDashboard />} />
              <Route path="/operations" element={<OperationsDashboard />} />
            </Routes>
          </main>
        </div>
        <Toaster position="top-right" />
      </div>
    </BrowserRouter>
  );
}

export default App;
