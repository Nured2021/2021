import { downloadUrl } from "../api/documentApi";
import { useState } from "react";
import styles from "./PreviewPanel.module.css";

const MODULE_LABELS = {
  document:     "📄 Documents AI",
  slides:       "📽️ Slides AI",
  excel:        "📊 Excel AI",
  upload:       "📁 Upload AI",
  professor:    "🎓 Senior Professor AI",
  teacher:      "📚 Teacher AI",
  exam:         "📝 Exam Prep AI",
  simulation:   "💼 Simulation AI",
  court:        "⚖️ Court AI",
  student:      "🙋 Student Assistant AI",
  admin:        "🗂️ Admin AI",
  multilingual: "🌐 Languages AI",
  integrity:    "🛡️ Integrity AI",
  business:     "🏢 Business AI",
  research:     "🔬 Research AI",
  analytics:    "📈 Analytics AI",
  content:      "✍️ Content AI",
  course:       "🏫 Course Builder AI",
};

const FORMAT_ICONS = {
  doc: "📄", pdf: "📑", slides: "📽️", excel: "📊",
  edu: "🎓", business: "🏢", research: "🔬",
  analytics: "📈", content: "✍️", course: "🏫", upload: "📁",
  multilingual: "🌐",
};

function StructuredContent({ content }) {
  if (!content) return null;
  return (
    <div className={styles.structuredContent}>
      {content.split("\n").map((line, i) => {
        const t = line.trim();
        if (!t) return <div key={i} className={styles.spacer} />;
        if (/^#{1,3}\s/.test(t))
          return <p key={i} className={styles.subHeading}>{t.replace(/^#{1,3}\s/, "")}</p>;
        if (t.length < 65 && t === t.toUpperCase() && /[A-Z]/.test(t))
          return <p key={i} className={styles.subHeading}>{t}</p>;
        if (/^[-•*✅❌⚠□✓✗△]\s/.test(t))
          return <p key={i} className={styles.bullet}>{t.replace(/^[-•*✅❌⚠□✓✗△]\s/, "• ")}</p>;
        if (t.includes("|"))
          return <p key={i} className={styles.tableRow}>{t}</p>;
        return <p key={i} className={styles.line}>{t}</p>;
      })}
    </div>
  );
}

function WorkspaceItem({ item, onLoad }) {
  return (
    <div className={styles.wsItem}>
      <button className={styles.wsLoadBtn} onClick={() => onLoad(item)} title="Load this item">
        <span className={styles.wsIcon}>{FORMAT_ICONS[item.format] || "📄"}</span>
        <span className={styles.wsName}>{item.name}</span>
      </button>
      <div className={styles.wsActions}>
        {item.pdf_url  && <a href={downloadUrl(item.pdf_url)}  download className={`${styles.wsBtn} ${styles.pdf}`}>PDF</a>}
        {item.docx_url && <a href={downloadUrl(item.docx_url)} download className={`${styles.wsBtn} ${styles.docx}`}>.docx</a>}
        {item.pptx_url && <a href={downloadUrl(item.pptx_url)} download className={`${styles.wsBtn} ${styles.pptx}`}>.pptx</a>}
        {item.xlsx_url && <a href={downloadUrl(item.xlsx_url)} download className={`${styles.wsBtn} ${styles.xlsx}`}>.xlsx</a>}
      </div>
    </div>
  );
}

function WorkspaceSection({ files, onLoad }) {
  return (
    <div className={styles.workspace}>
      <p className={styles.wsTitle}>🗂️ Workspace History ({files.length})</p>
      {files.map((item) => (
        <WorkspaceItem key={item.id} item={item} onLoad={onLoad} />
      ))}
    </div>
  );
}

export default function PreviewPanel({
  result, error, loading, workspaceFiles, onLoadWorkspaceItem,
  onGenerateSlides, onGenerateExcel, currentPrompt,
}) {
  const hasWorkspace = workspaceFiles && workspaceFiles.length > 0;

  if (loading) {
    return (
      <div className={`${styles.panel} ${styles.center}`}>
        <div className={styles.pulse}>✦</div>
        <p className={styles.loadingText}>AI is working on your request…</p>
        <p className={styles.loadingHint}>Generating real content, formulas, and files</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className={`${styles.panel} ${styles.center}`}>
        <p className={styles.error}>⚠ {error}</p>
        {hasWorkspace && <WorkspaceSection files={workspaceFiles} onLoad={onLoadWorkspaceItem} />}
      </div>
    );
  }

  if (!result) {
    return (
      <div className={styles.panel}>
        <div className={styles.emptyState}>
          <div className={styles.emptyIcon}>✦</div>
          <p className={styles.placeholder}>Your AI-generated content will appear here.</p>
          <p className={styles.emptyHint}>
            Choose a tool from the sidebar, type your request, and click Generate.
          </p>
        </div>
        {hasWorkspace && <WorkspaceSection files={workspaceFiles} onLoad={onLoadWorkspaceItem} />}
      </div>
    );
  }

  const pdfHref  = result.pdf_url  ? downloadUrl(result.pdf_url)  : null;
  const docxHref = result.docx_url ? downloadUrl(result.docx_url) : null;
  const pptxHref = result.pptx_url ? downloadUrl(result.pptx_url) : null;
  const xlsxHref = result.xlsx_url ? downloadUrl(result.xlsx_url) : null;
  const moduleLabel = result.module_name || (result.module ? MODULE_LABELS[result.module] : null);
  const showSlides = !pptxHref && result.module !== "slides" && onGenerateSlides;
  const showExcel  = !xlsxHref && result.module !== "excel"  && onGenerateExcel;

  return (
    <div className={styles.panel}>
      <div className={styles.header}>
        {moduleLabel && <span className={styles.moduleBadge}>{moduleLabel}</span>}
        <h3 className={styles.docTitle}>{result.title}</h3>
        <div className={styles.actions}>
          {pdfHref  && <a href={pdfHref}  download className={`${styles.btn} ${styles.pdf}`}>⬇ PDF</a>}
          {docxHref && <a href={docxHref} download className={`${styles.btn} ${styles.docx}`}>⬇ Word</a>}
          {pptxHref && <a href={pptxHref} download className={`${styles.btn} ${styles.pptx}`}>⬇ Slides</a>}
          {xlsxHref && <a href={xlsxHref} download className={`${styles.btn} ${styles.xlsx}`}>⬇ Excel</a>}
        </div>
        {(showSlides || showExcel) && (
          <div className={styles.workflowRow}>
            <span className={styles.workflowLabel}>Convert to:</span>
            {showSlides && (
              <button
                className={`${styles.workflowBtn} ${styles.pptxWf}`}
                onClick={() => onGenerateSlides(currentPrompt || result.title)}
                title="Turn this into a slide presentation"
              >
                📽️ Slides
              </button>
            )}
            {showExcel && (
              <button
                className={`${styles.workflowBtn} ${styles.xlsxWf}`}
                onClick={() => onGenerateExcel(currentPrompt || result.title)}
                title="Extract data into a spreadsheet"
              >
                📊 Excel
              </button>
            )}
          </div>
        )}
        {/* ── Integrations row ──────────────────────────────────────── */}
        <IntegrationsBar result={result} pdfHref={pdfHref} />
      </div>

      <div className={styles.content}>
        {result.sections && result.sections.map((sec, i) => (
          <div key={i} className={styles.section}>
            <h4 className={styles.sectionHeading}>{sec.heading}</h4>
            <StructuredContent content={sec.content} />
          </div>
        ))}
      </div>

      {hasWorkspace && <WorkspaceSection files={workspaceFiles} onLoad={onLoadWorkspaceItem} />}
    </div>
  );
}

/* ─── Integrations Bar ─────────────────────────────────────────────────── */
const API_BASE_INT = import.meta.env.VITE_API_URL || "";

function IntegrationsBar({ result, pdfHref }) {
  const [open,      setOpen]      = useState(false);
  const [tab,       setTab]       = useState("slack");
  const [slackUrl,  setSlackUrl]  = useState("");
  const [zoomTopic, setZoomTopic] = useState(result?.title || "");
  const [zoomTime,  setZoomTime]  = useState("");
  const [zoomToken, setZoomToken] = useState("");
  const [gdToken,   setGdToken]   = useState("");
  const [busy,      setBusy]      = useState(false);
  const [msg,       setMsg]       = useState("");

  const authHdr = () => {
    const t = localStorage.getItem("easy_ai_token");
    return t ? { Authorization: `Bearer ${t}` } : {};
  };

  const sendSlack = async () => {
    if (!slackUrl) return;
    setBusy(true);
    try {
      const r = await fetch(`${API_BASE_INT}/api/integrations/slack/notify`, {
        method: "POST",
        headers: { "Content-Type": "application/json", ...authHdr() },
        body: JSON.stringify({ webhook_url: slackUrl, message: `✅ *${result.title}* is ready!`,
          document_title: result.title, document_url: pdfHref || "" }),
      });
      const d = await r.json();
      setMsg(d.success ? "✅ Sent to Slack!" : "⚠ Failed.");
    } catch { setMsg("⚠ Error."); } finally { setBusy(false); }
  };

  const scheduleZoom = async () => {
    if (!zoomToken || !zoomTopic || !zoomTime) return;
    setBusy(true);
    try {
      const r = await fetch(`${API_BASE_INT}/api/integrations/zoom/schedule`, {
        method: "POST",
        headers: { "Content-Type": "application/json", ...authHdr() },
        body: JSON.stringify({ access_token: zoomToken, topic: zoomTopic,
          start_time: zoomTime, duration: 60 }),
      });
      const d = await r.json();
      setMsg(d.join_url ? `✅ ${d.join_url}` : "⚠ Failed.");
    } catch { setMsg("⚠ Error."); } finally { setBusy(false); }
  };

  const uploadDrive = async () => {
    if (!gdToken || !pdfHref) return;
    setBusy(true);
    try {
      const r = await fetch(`${API_BASE_INT}/api/integrations/google-drive/upload`, {
        method: "POST",
        headers: { "Content-Type": "application/json", ...authHdr() },
        body: JSON.stringify({ access_token: gdToken, file_url: pdfHref,
          filename: `${result.title}.pdf` }),
      });
      const d = await r.json();
      setMsg(d.drive_url ? `✅ ${d.drive_url}` : "⚠ Failed.");
    } catch { setMsg("⚠ Error."); } finally { setBusy(false); }
  };

  return (
    <div className={styles.integBar}>
      <button className={styles.integToggle} onClick={() => { setOpen(o => !o); setMsg(""); }}>
        🔗 Integrations {open ? "▲" : "▼"}
      </button>
      {open && (
        <div className={styles.integPanel}>
          <div className={styles.integTabs}>
            {[["slack","💬 Slack"],["zoom","🎥 Zoom"],["drive","☁️ Drive"]].map(([id,lbl]) => (
              <button key={id} className={`${styles.integTab} ${tab===id?styles.integTabActive:""}`}
                onClick={() => { setTab(id); setMsg(""); }}>{lbl}</button>
            ))}
          </div>
          {tab === "slack" && (
            <div className={styles.integForm}>
              <p className={styles.integHint}>Paste your Slack Incoming Webhook URL.</p>
              <input className={styles.integInput} placeholder="https://hooks.slack.com/services/…"
                value={slackUrl} onChange={e => setSlackUrl(e.target.value)} />
              <button className={styles.integBtn} onClick={sendSlack} disabled={busy||!slackUrl}>
                {busy?"Sending…":"Send Notification"}</button>
            </div>
          )}
          {tab === "zoom" && (
            <div className={styles.integForm}>
              <p className={styles.integHint}>Schedule a Zoom meeting to review this document.</p>
              <input className={styles.integInput} placeholder="Zoom OAuth Bearer token"
                value={zoomToken} onChange={e => setZoomToken(e.target.value)} />
              <input className={styles.integInput} placeholder="Meeting topic"
                value={zoomTopic} onChange={e => setZoomTopic(e.target.value)} />
              <input className={styles.integInput} type="datetime-local"
                value={zoomTime.replace(":00Z","")} onChange={e => setZoomTime(e.target.value+":00Z")} />
              <button className={styles.integBtn} onClick={scheduleZoom}
                disabled={busy||!zoomToken||!zoomTopic||!zoomTime}>
                {busy?"Scheduling…":"Schedule Meeting"}</button>
            </div>
          )}
          {tab === "drive" && (
            <div className={styles.integForm}>
              <p className={styles.integHint}>Upload the PDF to your Google Drive.
                {!pdfHref&&" (Generate a PDF first.)"}</p>
              <input className={styles.integInput} placeholder="Google OAuth access token"
                value={gdToken} onChange={e => setGdToken(e.target.value)} />
              <button className={styles.integBtn} onClick={uploadDrive}
                disabled={busy||!gdToken||!pdfHref}>
                {busy?"Uploading…":"Upload to Drive"}</button>
            </div>
          )}
          {msg && <p className={styles.integMsg}>{msg}</p>}
        </div>
      )}
    </div>
  );
}
