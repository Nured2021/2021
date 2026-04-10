import { useRef, useState } from "react";
import Sidebar from "./components/Sidebar";
import PromptPanel from "./components/PromptPanel";
import PreviewPanel from "./components/PreviewPanel";
import { buildRequest } from "./api/buildApi";
import { generateEducation, uploadMaterial } from "./api/educationApi";
import "./App.css";

// Map sidebar doc-format pills to the /api/build mode string
const FORMAT_TO_BUILD_MODE = {
  doc:    "document",
  pdf:    "document",
  slides: "presentation",
  excel:  "spreadsheet",
};

function App() {
  const [activeTab, setActiveTab]           = useState("document");
  const [docFormat, setDocFormat]           = useState("doc");
  const [loading, setLoading]               = useState(false);
  const [result, setResult]                 = useState(null);
  const [error, setError]                   = useState(null);
  const [status, setStatus]                 = useState("Ready");
  const [workspaceFiles, setWorkspaceFiles] = useState([]);
  const [uploadedFileName, setUploadedFileName] = useState("");
  // Workspace click-to-load: holds a prompt string to inject into PromptPanel
  const [pendingPrompt, setPendingPrompt]   = useState(null);
  const fileInputRef = useRef(null);

  const isEducationTab = activeTab.startsWith("edu_");

  const handleGenerate = async (prompt) => {
    setLoading(true);
    setError(null);
    setResult(null);
    setStatus("Generating…");
    try {
      let data;
      if (isEducationTab) {
        // Education modules keep their dedicated endpoint for richer edu-specific output
        const module = activeTab.replace("edu_", "");
        data = await generateEducation({ prompt, module });
      } else {
        // All office/document requests go through the unified /api/build endpoint
        const mode = FORMAT_TO_BUILD_MODE[docFormat] || "auto";
        data = await buildRequest(prompt, mode);
      }
      setResult(data);

      // Add to workspace history
      setWorkspaceFiles((prev) => [
        {
          id: Date.now(),
          name: data.title || `${docFormat.toUpperCase()} Output`,
          format: isEducationTab ? "edu" : docFormat,
          prompt,
          pdf_url:  data.pdf_url  || null,
          docx_url: data.docx_url || null,
          pptx_url: data.pptx_url || null,
          xlsx_url: data.xlsx_url || null,
          _result: data,
        },
        ...prev.slice(0, 9),
      ]);
      setStatus("Done");
    } catch (err) {
      setError(err.message);
      setStatus("Error");
    } finally {
      setLoading(false);
    }
  };

  const handleUpload = async (e) => {
    const file = e.target.files?.[0];
    if (!file) return;
    setUploadedFileName(file.name);
    setLoading(true);
    setError(null);
    setResult(null);
    setStatus("Uploading…");
    try {
      const module = isEducationTab ? activeTab.replace("edu_", "") : "student";
      const data = await uploadMaterial(file, module);
      setResult(data);
      setWorkspaceFiles((prev) => [
        {
          id: Date.now(),
          name: data.title || `Upload: ${file.name}`,
          format: "edu",
          prompt: `Summarise uploaded file: ${file.name}`,
          pdf_url:  data.pdf_url  || null,
          docx_url: data.docx_url || null,
          pptx_url: null,
          xlsx_url: null,
          _result: data,
        },
        ...prev.slice(0, 9),
      ]);
      setStatus("Upload complete");
    } catch (err) {
      setError(err.message);
      setStatus("Error");
    } finally {
      setLoading(false);
      // reset so same file can be re-uploaded
      if (fileInputRef.current) fileInputRef.current.value = "";
    }
  };

  const handleTranslate = async (currentPrompt) => {
    if (!currentPrompt.trim()) return;
    const translatePrompt = `Translate to clear professional English:\n\n${currentPrompt}`;
    setLoading(true);
    setError(null);
    setResult(null);
    setStatus("Translating…");
    try {
      const data = await generateEducation({ prompt: translatePrompt, module: "multilingual" });
      setResult(data);
      setWorkspaceFiles((prev) => [
        {
          id: Date.now(),
          name: data.title || "Translation",
          format: "edu",
          prompt: translatePrompt,
          pdf_url:  data.pdf_url  || null,
          docx_url: data.docx_url || null,
          pptx_url: null,
          xlsx_url: null,
          _result: data,
        },
        ...prev.slice(0, 9),
      ]);
      setStatus("Translated");
    } catch (err) {
      setError(err.message);
      setStatus("Error");
    } finally {
      setLoading(false);
    }
  };

  const handleTabSelect = (tab) => {
    if (tab === "uploads") {
      // Trigger file picker
      fileInputRef.current?.click();
      return;
    }
    setActiveTab(tab);
    setResult(null);
    setError(null);
    setStatus("Ready");
  };

  // Workspace click-to-load: restore prompt + preview
  const handleLoadWorkspaceItem = (item) => {
    if (item._result) setResult(item._result);
    if (item.prompt)  setPendingPrompt(item.prompt);
  };

  return (
    <div className="layout">
      <Sidebar
        active={activeTab}
        onSelect={handleTabSelect}
        docFormat={docFormat}
        onDocFormat={setDocFormat}
      />
      <main className="main">
        <PromptPanel
          docType={activeTab}
          docFormat={docFormat}
          onGenerate={handleGenerate}
          onTranslate={handleTranslate}
          loading={loading}
          status={status}
          uploadedFileName={uploadedFileName}
          externalPrompt={pendingPrompt}
          onPromptConsumed={() => setPendingPrompt(null)}
        />
      </main>
      <PreviewPanel
        result={result}
        error={error}
        loading={loading}
        workspaceFiles={workspaceFiles}
        onLoadWorkspaceItem={handleLoadWorkspaceItem}
      />
      {/* Hidden file input for uploads */}
      <input
        ref={fileInputRef}
        type="file"
        accept=".txt,.md,.csv,.json,.pdf,.docx"
        style={{ display: "none" }}
        onChange={handleUpload}
      />
    </div>
  );
}

export default App;
