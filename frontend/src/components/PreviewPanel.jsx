import { downloadUrl } from "../api/documentApi";
import styles from "./PreviewPanel.module.css";

const MODULE_LABELS = {
  professor:    "🎓 Senior Professor AI",
  teacher:      "📚 Teacher AI",
  exam:         "📝 Exam Prep AI",
  simulation:   "💼 Simulation AI",
  court:        "⚖️ Court AI",
  student:      "🙋 Student Assistant AI",
  admin:        "🗂️ Admin AI",
  multilingual: "🌐 Multilingual AI",
  integrity:    "🛡️ Integrity AI",
};

const FORMAT_ICONS = {
  doc:    "📄",
  pdf:    "📑",
  slides: "📽️",
  excel:  "📊",
  edu:    "🎓",
};

// Render a section's content with simple heading detection
function StructuredContent({ content }) {
  if (!content) return null;
  const lines = content.split("\n");
  return (
    <div className={styles.structuredContent}>
      {lines.map((line, i) => {
        const trimmed = line.trim();
        if (!trimmed) return <div key={i} className={styles.spacer} />;
        // Detect markdown-style headings or ALL-CAPS short lines as sub-headings
        if (/^#{1,3}\s/.test(trimmed)) {
          return (
            <p key={i} className={styles.subHeading}>
              {trimmed.replace(/^#{1,3}\s/, "")}
            </p>
          );
        }
        if (trimmed.length < 60 && trimmed === trimmed.toUpperCase() && /[A-Z]/.test(trimmed)) {
          return <p key={i} className={styles.subHeading}>{trimmed}</p>;
        }
        // Bullet lines
        if (/^[-•*]\s/.test(trimmed)) {
          return (
            <p key={i} className={styles.bullet}>
              {trimmed.replace(/^[-•*]\s/, "• ")}
            </p>
          );
        }
        return <p key={i} className={styles.line}>{trimmed}</p>;
      })}
    </div>
  );
}

function WorkspaceItem({ item, onLoad }) {
  return (
    <div className={styles.wsItem}>
      <button
        className={styles.wsLoadBtn}
        onClick={() => onLoad(item)}
        title="Load this item"
      >
        <span className={styles.wsIcon}>{FORMAT_ICONS[item.format] || "📄"}</span>
        <span className={styles.wsName}>{item.name}</span>
      </button>
      <div className={styles.wsActions}>
        {item.pdf_url && (
          <a
            href={downloadUrl(item.pdf_url)}
            download
            className={`${styles.wsBtn} ${styles.pdf}`}
            title="Download PDF"
          >
            PDF
          </a>
        )}
        {item.docx_url && (
          <a
            href={downloadUrl(item.docx_url)}
            download
            className={`${styles.wsBtn} ${styles.docx}`}
            title="Download Word"
          >
            .docx
          </a>
        )}
        {item.pptx_url && (
          <a
            href={downloadUrl(item.pptx_url)}
            download
            className={`${styles.wsBtn} ${styles.pptx}`}
            title="Download Slides"
          >
            .pptx
          </a>
        )}
        {item.xlsx_url && (
          <a
            href={downloadUrl(item.xlsx_url)}
            download
            className={`${styles.wsBtn} ${styles.xlsx}`}
            title="Download Spreadsheet"
          >
            .xlsx
          </a>
        )}
      </div>
    </div>
  );
}

export default function PreviewPanel({ result, error, loading, workspaceFiles, onLoadWorkspaceItem }) {
  const hasWorkspace = workspaceFiles && workspaceFiles.length > 0;

  if (loading) {
    return (
      <div className={`${styles.panel} ${styles.center}`}>
        <div className={styles.pulse}>✦</div>
        <p className={styles.loadingText}>Generating your document…</p>
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
          <p className={styles.placeholder}>
            Your document preview will appear here.
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
  const moduleLabel = result.module ? MODULE_LABELS[result.module] : null;

  return (
    <div className={styles.panel}>
      <div className={styles.header}>
        {moduleLabel && (
          <span className={styles.moduleBadge}>{moduleLabel}</span>
        )}
        <h3 className={styles.docTitle}>{result.title}</h3>
        <div className={styles.actions}>
          {pdfHref  && <a href={pdfHref}  download className={`${styles.btn} ${styles.pdf}`}>⬇ PDF</a>}
          {docxHref && <a href={docxHref} download className={`${styles.btn} ${styles.docx}`}>⬇ Word</a>}
          {pptxHref && <a href={pptxHref} download className={`${styles.btn} ${styles.pptx}`}>⬇ Slides</a>}
          {xlsxHref && <a href={xlsxHref} download className={`${styles.btn} ${styles.xlsx}`}>⬇ Excel</a>}
        </div>
      </div>

      <div className={styles.content}>
        {result.sections.map((sec, i) => (
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

function WorkspaceSection({ files, onLoad }) {
  return (
    <div className={styles.workspace}>
      <p className={styles.wsTitle}>🗂️ Workspace</p>
      {files.map((item) => (
        <WorkspaceItem key={item.id} item={item} onLoad={onLoad} />
      ))}
    </div>
  );
}
