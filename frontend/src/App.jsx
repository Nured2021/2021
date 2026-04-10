import { useState } from "react";
import Sidebar from "./components/Sidebar";
import PromptPanel from "./components/PromptPanel";
import PreviewPanel from "./components/PreviewPanel";
import { generateDocument } from "./api/documentApi";
import "./App.css";

function App() {
  const [activeTab, setActiveTab] = useState("document");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  const handleGenerate = async (prompt) => {
    setLoading(true);
    setError(null);
    setResult(null);
    try {
      const data = await generateDocument({ prompt, docType: activeTab });
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
