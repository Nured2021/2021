import { useEffect, useState } from "react";
import { fetchMaterials } from "../api/educationApi";
import styles from "./MaterialPicker.module.css";

/**
 * Fetches uploaded materials from the server and lets the user pick one.
 * Calls onPick(promptSnippet) when a material is selected.
 */
export default function MaterialPicker({ onPick }) {
  const [materials, setMaterials] = useState([]);
  const [open, setOpen]           = useState(false);
  const [loading, setLoading]     = useState(false);
  const [error, setError]         = useState(null);

  const loadMaterials = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await fetchMaterials();
      setMaterials(data || []);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleToggle = () => {
    if (!open) loadMaterials();
    setOpen((v) => !v);
  };

  const handleSelect = (mat) => {
    onPick(`Based on the uploaded file "${mat.filename}":\n\n`);
    setOpen(false);
  };

  return (
    <div className={styles.wrapper}>
      <button
        type="button"
        className={styles.toggleBtn}
        onClick={handleToggle}
        title="Use an uploaded material"
      >
        📎 My Uploads {open ? "▲" : "▼"}
      </button>

      {open && (
        <div className={styles.dropdown}>
          {loading && <p className={styles.info}>Loading…</p>}
          {error   && <p className={styles.error}>⚠ {error}</p>}
          {!loading && !error && materials.length === 0 && (
            <p className={styles.info}>No uploads yet.</p>
          )}
          {materials.map((mat) => (
            <button
              key={mat.id}
              type="button"
              className={styles.item}
              onClick={() => handleSelect(mat)}
              title={`Module: ${mat.module} — ${mat.timestamp}`}
            >
              <span className={styles.icon}>📄</span>
              <span className={styles.name}>{mat.filename}</span>
              <span className={styles.module}>{mat.module}</span>
            </button>
          ))}
        </div>
      )}
    </div>
  );
}
