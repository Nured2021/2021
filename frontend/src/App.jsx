import { useState } from "react";
import Sidebar from "./components/Sidebar";
import PromptPanel from "./components/PromptPanel";
import PreviewPanel from "./components/PreviewPanel";
import { generateDocument } from "./api/documentApi";
import { generateEducation } from "./api/educationApi";
import "./App.css";

function App() {
  const [activeTab, setActiveTab] = useState("document");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  const isEducationTab = activeTab.startsWith("edu_");

  const handleGenerate = async (prompt) => {
    setLoading(true);
    setError(null);
    setResult(null);
    try {
      let data;
      if (isEducationTab) {
        // Strip the "edu_" prefix to get the module id
        const module = activeTab.replace("edu_", "");
        data = await generateEducation({ prompt, module });
      } else {
        data = await generateDocument({ prompt, docType: activeTab });
      }
      setResult(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleTabSelect = (tab) => {
    if (tab === "uploads") return;
    setActiveTab(tab);
    setResult(null);
    setError(null);
  };

  return (
    <div className="layout">
      <Sidebar active={activeTab} onSelect={handleTabSelect} />
      <main className="main">
        <PromptPanel
          docType={activeTab}
          onGenerate={handleGenerate}
          loading={loading}
        />
      </main>
      <PreviewPanel result={result} error={error} loading={loading} />
    </div>
  );
}

export default App;
