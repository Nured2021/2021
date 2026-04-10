import { useState } from "react";
import styles from "./PromptPanel.module.css";
import ChatPanel from "./ChatPanel";
import MaterialPicker from "./MaterialPicker";

const FEATURE_CARDS = [
  {
    icon: "📄",
    title: "Built for Documents",
    desc: "Generate professional docs, reports, contracts, and academic content with a single prompt.",
  },
  {
    icon: "🗂️",
    title: "AI-Managed Workspace",
    desc: "Your generated files are tracked in the workspace. Download PDF or Word any time.",
  },
  {
    icon: "🧠",
    title: "Learns From You",
    desc: "Upload your own files and let the AI summarise, explain, and build study guides from them.",
  },
];

const EDU_PLACEHOLDERS = {
  edu_professor:    "e.g. Create a syllabus for a Business Law course at postgraduate level...",
  edu_teacher:      "e.g. Lesson plan for teaching recursion in Computer Science to Year 12...",
  edu_exam:         "e.g. Generate a 20-question quiz on contract law with an answer key...",
  edu_simulation:   "e.g. Business case study on a startup facing a regulatory challenge...",
  edu_court:        "e.g. Mock trial for a contract dispute between two companies...",
  edu_student:      "e.g. Create a study guide on corporate governance for my finals...",
  edu_admin:        "e.g. Build a weekly class schedule and assignment tracker for fall semester...",
  edu_multilingual: "e.g. Translate this academic abstract into French...",
  edu_integrity:    "e.g. Review my essay for plagiarism guidance and citation issues...",
};

const DOC_PLACEHOLDERS = {
  presentation: "e.g. Quarterly business review for Q3 2024...",
  excel:        "e.g. Monthly budget tracker for a small team...",
};

const EDU_TITLES = {
  edu_professor:    "Senior Professor AI",
  edu_teacher:      "Teacher AI",
  edu_exam:         "Exam Prep AI",
  edu_simulation:   "Real World Simulation AI",
  edu_court:        "Court AI",
  edu_student:      "Student Assistant AI",
  edu_admin:        "Administrative AI",
  edu_multilingual: "Multilingual AI",
  edu_integrity:    "Academic Integrity AI",
};

const FORMAT_LABELS = {
  doc:    "Word Document",
  pdf:    "PDF Document",
  slides: "Presentation",
  excel:  "Spreadsheet",
};

export default function PromptPanel({
  docType,
  docFormat,
  onGenerate,
  onTranslate,
  loading,
  status,
  uploadedFileName,
  externalPrompt,      // workspace click sets this
  onPromptConsumed,    // called after externalPrompt has been applied
}) {
  const [prompt, setPrompt] = useState("");

  // Apply an externally-set prompt (e.g. from workspace click)
  if (externalPrompt !== undefined && externalPrompt !== null && externalPrompt !== prompt) {
    setPrompt(externalPrompt);
    onPromptConsumed?.();
  }

  const handleSubmit = (e) => {
    e.preventDefault();
    if (prompt.trim()) onGenerate(prompt.trim());
  };

  const handleTranslate = () => {
    if (prompt.trim()) onTranslate(prompt.trim());
  };

  const handleMaterialPick = (snippet) => {
    setPrompt((prev) => snippet + (prev ? prev : ""));
  };

  const isEducation = docType.startsWith("edu_");
  const title = isEducation
    ? EDU_TITLES[docType] || "Education AI"
    : FORMAT_LABELS[docFormat] || "Generate Document";

  const subtitle = isEducation
    ? "Describe your academic request and let AI create it for you."
    : "Describe what you want and let AI create it for you.";

  const placeholder =
    EDU_PLACEHOLDERS[docType] ||
    DOC_PLACEHOLDERS[docType] ||
    "e.g. Write a project proposal for a new mobile app...";

  const showFeatureCards = !loading && !prompt.trim();
  const chatModule = isEducation ? docType.replace("edu_", "") : null;

  return (
    <div className={styles.panel}>
      <div className={styles.header}>
        <h2 className={styles.title}>{title}</h2>
        <p className={styles.subtitle}>{subtitle}</p>
        {uploadedFileName && (
          <span className={styles.uploadBadge}>📎 {uploadedFileName}</span>
        )}
      </div>

      <form className={styles.form} onSubmit={handleSubmit}>
        <textarea
          className={styles.textarea}
          value={prompt}
          onChange={(e) => setPrompt(e.target.value)}
          placeholder={placeholder}
          rows={8}
          disabled={loading}
        />

        {/* Material picker row */}
        <div className={styles.materialRow}>
          <MaterialPicker onPick={handleMaterialPick} />
        </div>

        <div className={styles.actionRow}>
          <button
            type="submit"
            className={styles.button}
            disabled={loading || !prompt.trim()}
          >
            {loading ? (
              <>
                <span className={styles.spinner} />
                {status || "Generating…"}
              </>
            ) : (
              <>✦ Generate</>
            )}
          </button>

          <button
            type="button"
            className={`${styles.button} ${styles.outlineBtn}`}
            disabled={loading || !prompt.trim()}
            onClick={handleTranslate}
            title="Translate content to English"
          >
            🌐 Translate
          </button>
        </div>

        {status && status !== "Ready" && (
          <p className={styles.statusText}>{status}</p>
        )}
      </form>

      {showFeatureCards && (
        <div className={styles.cards}>
          {FEATURE_CARDS.map((card) => (
            <div key={card.title} className={styles.card}>
              <span className={styles.cardIcon}>{card.icon}</span>
              <div>
                <p className={styles.cardTitle}>{card.title}</p>
                <p className={styles.cardDesc}>{card.desc}</p>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Education chat panel — shown for all edu_ tabs */}
      {chatModule && <ChatPanel module={chatModule} />}
    </div>
  );
}
