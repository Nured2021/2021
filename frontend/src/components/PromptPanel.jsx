import { useState } from "react";
import styles from "./PromptPanel.module.css";

export default function PromptPanel({ docType, onGenerate, loading }) {
  const [prompt, setPrompt] = useState("");

  const handleSubmit = (e) => {
    e.preventDefault();
    if (prompt.trim()) onGenerate(prompt.trim());
  };

  const placeholder =
    docType === "presentation"
      ? "e.g. Quarterly business review for Q3 2024..."
      : docType === "excel"
      ? "e.g. Monthly budget tracker for a small team..."
      : "e.g. Write a project proposal for a new mobile app...";

  return (
    <div className={styles.panel}>
      <div className={styles.header}>
        <h2 className={styles.title}>Generate Document</h2>
        <p className={styles.subtitle}>
          Describe what you want and let AI create it for you.
        </p>
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
