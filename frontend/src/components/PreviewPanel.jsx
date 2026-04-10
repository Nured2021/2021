import { downloadUrl } from "../api/documentApi";
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
