import { useRef, useState } from "react";
import Sidebar from "./components/Sidebar";
import PromptPanel from "./components/PromptPanel";
import PreviewPanel from "./components/PreviewPanel";
import { buildRequest, uploadFile } from "./api/buildApi";
import { generateEducation } from "./api/educationApi";
import "./App.css";

/* ── Module routing table ───────────────────────────────────────────
   Maps each sidebar tab ID → the module key sent to /api/build.
   Education tabs strip the "edu_" prefix and go via /education/generate.
   Business & Pro tabs go directly to /api/build with their module key.
──────────────────────────────────────────────────────────────────── */
const TAB_TO_MODULE = {
  document:         "document",
  excel:            "excel",
  presentation:     "slides",
  // Business & Pro tabs
  business:         "business",
  research:         "research",
  analytics:        "analytics",
  content:          "content",
  course:           "course",
};

const FORMAT_TO_MODULE = {
  doc:    "document",
  pdf:    "document",
  slides: "slides",
  excel:  "excel",
};

// Which tabs render using the education API (for richer edu output)
const IS_EDU_TAB = (tab) => tab.startsWith("edu_");
// Which tabs go through /api/build (all non-edu tabs except "uploads")
const IS_BUILD_TAB = (tab) => !IS_EDU_TAB(tab) && tab !== "uploads";

/* Status message sequences for animated feedback */
const STATUS_SEQ = {
  default:     ["Analysing your request…", "Routing to specialist AI…", "Generating content…", "Formatting output…", "Almost done…"],
  excel:       ["Parsing your request…", "Building data structure…", "Applying formulas…", "Creating charts…", "Finalising spreadsheet…"],
  slides:      ["Understanding your topic…", "Designing slide layouts…", "Writing content…", "Adding speaker notes…", "Rendering presentation…"],
  business:    ["Analysing market context…", "Building business case…", "Running financial model…", "Formatting strategy…", "Almost done…"],
  research:    ["Reviewing research context…", "Structuring methodology…", "Building literature review…", "Formatting paper…", "Almost done…"],
  analytics:   ["Loading data model…", "Running analysis…", "Identifying trends…", "Building KPI dashboard…", "Finalising insights…"],
  court:       ["Analysing legal context…", "Drafting legal arguments…", "Citing relevant law…", "Formatting document…", "Almost done…"],
  upload:      ["Reading file…", "Extracting text…", "Identifying key topics…", "Generating summary…", "Almost done…"],
};

function App() {
  const [activeTab, setActiveTab]     = useState("document");
  const [docFormat, setDocFormat]     = useState("doc");
  const [loading, setLoading]         = useState(false);
  const [result, setResult]           = useState(null);
  const [error, setError]             = useState(null);
  const [status, setStatus]           = useState("Ready");
  const [workspaceFiles, setWorkspaceFiles] = useState([]);
  const [uploadedFileName, setUploadedFileName] = useState("");
  const [pendingPrompt, setPendingPrompt] = useState(null);
  const fileInputRef = useRef(null);
  const statusTimerRef = useRef(null);

  /* Animated status messages */
  const animateStatus = (module) => {
    const seq = STATUS_SEQ[module] || STATUS_SEQ.default;
    let i = 0;
    setStatus(seq[0]);
    statusTimerRef.current = setInterval(() => {
      i = (i + 1) % seq.length;
      setStatus(seq[i]);
    }, 1800);
  };
  const stopAnimation = () => {
    clearInterval(statusTimerRef.current);
    statusTimerRef.current = null;
  };

  /* Add entry to workspace history */
  const addToWorkspace = (data, prompt, format) => {
    setWorkspaceFiles((prev) => [
      {
        id: Date.now(),
        name: data.title || `${format.toUpperCase()} Output`,
        format,
        prompt,
        pdf_url:  data.pdf_url  || null,
        docx_url: data.docx_url || null,
        pptx_url: data.pptx_url || null,
        xlsx_url: data.xlsx_url || null,
        _result: data,
      },
      ...prev.slice(0, 19),
    ]);
  };

  /* ── Main generate handler ──────────────────────────────────── */
  const handleGenerate = async (prompt) => {
    setLoading(true);
    setError(null);
    setResult(null);

    let data;
    try {
      if (IS_EDU_TAB(activeTab)) {
        // Education tabs use /education/generate
        const module = activeTab.replace("edu_", "");
        animateStatus(module);
        data = await generateEducation({ prompt, module });

      } else {
        // All other tabs use /api/build — the Central Brain auto-routes
        const module = TAB_TO_MODULE[activeTab] || FORMAT_TO_MODULE[docFormat] || "auto";
        animateStatus(module);
        data = await buildRequest(prompt, module);
      }

      setResult(data);
      addToWorkspace(data, prompt, data.module || activeTab);
      setStatus("✓ Complete");
    } catch (err) {
      setError(err.message);
      setStatus("Error");
    } finally {
      stopAnimation();
      setLoading(false);
    }
  };

  /* ── Workflow automation: "Generate Slides from this" ───────── */
  const handleGenerateSlides = async (prompt) => {
    if (!result || !prompt) return;
    setLoading(true);
    setError(null);
    animateStatus("slides");
    try {
      const data = await buildRequest(
        `Convert the following content into a professional slide presentation:\n\n${result.body?.substring(0, 3000) || prompt}`,
        "slides"
      );
      setResult(data);
      addToWorkspace(data, prompt, "slides");
      setStatus("✓ Slides ready");
    } catch (err) {
      setError(err.message);
      setStatus("Error");
    } finally {
      stopAnimation();
      setLoading(false);
    }
  };

  /* ── Workflow automation: "Export to Excel" ─────────────────── */
  const handleGenerateExcel = async (prompt) => {
    if (!result || !prompt) return;
    setLoading(true);
    setError(null);
    animateStatus("excel");
    try {
      const data = await buildRequest(
        `Extract all data tables and structured information from the following content and build a spreadsheet:\n\n${result.body?.substring(0, 3000) || prompt}`,
        "excel"
      );
      setResult(data);
      addToWorkspace(data, prompt, "excel");
      setStatus("✓ Excel ready");
    } catch (err) {
      setError(err.message);
      setStatus("Error");
    } finally {
      stopAnimation();
      setLoading(false);
    }
  };

  /* ── Upload handler ─────────────────────────────────────────── */
  const handleUpload = async (e) => {
    const file = e.target.files?.[0];
    if (!file) return;
    setUploadedFileName(file.name);
    setLoading(true);
    setError(null);
    setResult(null);
    animateStatus("upload");

    try {
      const data = await uploadFile(file, "upload");
      setResult(data);
      addToWorkspace(data, `[Uploaded: ${file.name}]`, "upload");
      setStatus("✓ File summarised");
    } catch (err) {
      setError(err.message);
      setStatus("Error");
    } finally {
      stopAnimation();
      setLoading(false);
      if (fileInputRef.current) fileInputRef.current.value = "";
    }
  };

  /* ── Translate shortcut ─────────────────────────────────────── */
  const handleTranslate = async (currentPrompt) => {
    if (!currentPrompt.trim()) return;
    setLoading(true);
    setError(null);
    setResult(null);
    animateStatus("multilingual");
    try {
      const data = await generateEducation({
        prompt: `Translate the following into clear professional English and provide a bilingual glossary:\n\n${currentPrompt}`,
        module: "multilingual",
      });
      setResult(data);
      addToWorkspace(data, currentPrompt, "multilingual");
      setStatus("✓ Translated");
    } catch (err) {
      setError(err.message);
      setStatus("Error");
    } finally {
      stopAnimation();
      setLoading(false);
    }
  };

  /* ── Tab selection ──────────────────────────────────────────── */
  const handleTabSelect = (tab) => {
    if (tab === "uploads") {
      fileInputRef.current?.click();
      return;
    }
    setActiveTab(tab);
    setResult(null);
    setError(null);
    setStatus("Ready");
  };

  /* ── Workspace restore ──────────────────────────────────────── */
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
        onGenerateSlides={handleGenerateSlides}
        onGenerateExcel={handleGenerateExcel}
        currentPrompt={pendingPrompt}
      />
      {/* Hidden file input */}
      <input
        ref={fileInputRef}
        type="file"
        accept=".txt,.md,.csv,.json,.pdf,.docx,.xlsx"
        style={{ display: "none" }}
        onChange={handleUpload}
      />
    </div>
  );
}

export default App;
