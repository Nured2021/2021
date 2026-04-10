import { downloadUrl } from "../api/documentApi";
import styles from "./PreviewPanel.module.css";

export default function PreviewPanel({ result, error, loading }) {
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
      </div>
    );
  }

  if (!result) {
    return (
      <div className={`${styles.panel} ${styles.center}`}>
        <p className={styles.placeholder}>
          Your document preview will appear here.
        </p>
      </div>
    );
  }

  return (
    <div className={styles.panel}>
      <div className={styles.header}>
        <h3 className={styles.docTitle}>{result.title}</h3>
        <div className={styles.actions}>
          <a
            href={downloadUrl(result.pdf_url)}
            download
            className={`${styles.btn} ${styles.pdf}`}
          >
            ⬇ PDF
          </a>
          <a
            href={downloadUrl(result.docx_url)}
            download
            className={`${styles.btn} ${styles.docx}`}
          >
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
    </div>
  );
}
