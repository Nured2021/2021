import { useState } from "react";
import styles from "./PromptPanel.module.css";

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

export default function PromptPanel({ docType, onGenerate, loading }) {
  const [prompt, setPrompt] = useState("");

  const handleSubmit = (e) => {
    e.preventDefault();
    if (prompt.trim()) onGenerate(prompt.trim());
  };

  const isEducation = docType.startsWith("edu_");
  const title = isEducation
    ? EDU_TITLES[docType] || "Education AI"
    : "Generate Document";

  const subtitle = isEducation
    ? "Describe your academic request and let AI create it for you."
    : "Describe what you want and let AI create it for you.";

  const placeholder =
    EDU_PLACEHOLDERS[docType] ||
    DOC_PLACEHOLDERS[docType] ||
    "e.g. Write a project proposal for a new mobile app...";

  return (
    <div className={styles.panel}>
      <div className={styles.header}>
        <h2 className={styles.title}>{title}</h2>
        <p className={styles.subtitle}>{subtitle}</p>
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
        <button
          type="submit"
          className={styles.button}
          disabled={loading || !prompt.trim()}
        >
          {loading ? (
            <>
              <span className={styles.spinner} />
              Generating…
            </>
          ) : (
            <>✦ Generate</>
          )}
        </button>
      </form>
    </div>
  );
}
