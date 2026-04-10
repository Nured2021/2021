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

function WorkspaceItem({ item }) {
  return (
    <div className={styles.wsItem}>
      <span className={styles.wsIcon}>{FORMAT_ICONS[item.format] || "📄"}</span>
      <span className={styles.wsName}>{item.name}</span>
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
      </div>
    </div>
  );
}

export default function PreviewPanel({ result, error, loading, workspaceFiles }) {
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
        {hasWorkspace && <WorkspaceSection files={workspaceFiles} />}
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
        {hasWorkspace && <WorkspaceSection files={workspaceFiles} />}
      </div>
    );
  }

  const pdfHref  = downloadUrl(result.pdf_url);
  const docxHref = downloadUrl(result.docx_url);
  const moduleLabel = result.module ? MODULE_LABELS[result.module] : null;

  return (
    <div className={styles.panel}>
      <div className={styles.header}>
        {moduleLabel && (
          <span className={styles.moduleBadge}>{moduleLabel}</span>
        )}
        <h3 className={styles.docTitle}>{result.title}</h3>
        <div className={styles.actions}>
          <a href={pdfHref} download className={`${styles.btn} ${styles.pdf}`}>
            ⬇ PDF
          </a>
          <a href={docxHref} download className={`${styles.btn} ${styles.docx}`}>
            ⬇ Word
          </a>
        </div>
      </div>

      <div className={styles.content}>
        {result.sections.map((sec, i) => (
          <div key={i} className={styles.section}>
            <h4 className={styles.sectionHeading}>{sec.heading}</h4>
            <p className={styles.sectionContent}>{sec.content}</p>
          </div>
        ))}
      </div>

      {hasWorkspace && <WorkspaceSection files={workspaceFiles} />}
    </div>
  );
}

function WorkspaceSection({ files }) {
  return (
    <div className={styles.workspace}>
      <p className={styles.wsTitle}>🗂️ Workspace</p>
      {files.map((item) => (
        <WorkspaceItem key={item.id} item={item} />
      ))}
    </div>
  );
}
