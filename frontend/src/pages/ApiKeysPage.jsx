import { useEffect, useState } from "react";
import { useAuth } from "../context/AuthContext";
import styles from "./ApiKeysPage.module.css";

const API_BASE = import.meta.env.VITE_API_URL || "";

export default function ApiKeysPage({ onClose }) {
  const { authHeader } = useAuth();
  const [keys, setKeys]     = useState([]);
  const [name, setName]     = useState("My API Key");
  const [newKey, setNewKey] = useState(null);
  const [loading, setLoading] = useState(false);

  const load = () => {
    fetch(`${API_BASE}/api/keys`, { headers: authHeader() })
      .then((r) => r.ok ? r.json() : [])
      .then(setKeys)
      .catch(() => {});
  };

  useEffect(load, []);

  const create = async (e) => {
    e.preventDefault();
    setLoading(true);
    setNewKey(null);
    try {
      const r = await fetch(`${API_BASE}/api/keys`, {
        method: "POST",
        headers: { ...authHeader(), "Content-Type": "application/json" },
        body: JSON.stringify({ name }),
      });
      const data = await r.json();
      if (data.key) setNewKey(data.key);
      load();
    } finally {
      setLoading(false);
    }
  };

  const deleteKey = async (id) => {
    if (!confirm("Delete this API key?")) return;
    await fetch(`${API_BASE}/api/keys/${id}`, { method: "DELETE", headers: authHeader() });
    load();
  };

  return (
    <div className={styles.overlay}>
      <div className={styles.panel}>
        <button className={styles.close} onClick={onClose}>✕</button>
        <h2 className={styles.title}>🔑 API Keys</h2>
        <p className={styles.sub}>Use API keys to access Easy AI from your own applications.</p>

        <form className={styles.form} onSubmit={create}>
          <input className={styles.input} value={name}
            onChange={(e) => setName(e.target.value)} placeholder="Key name" />
          <button className={styles.btn} type="submit" disabled={loading}>
            {loading ? "Creating…" : "+ Create Key"}
          </button>
        </form>

        {newKey && (
          <div className={styles.newKey}>
            <p className={styles.newKeyLabel}>✅ Your new API key (copy now — shown once):</p>
            <code className={styles.keyCode}>{newKey}</code>
            <pre className={styles.example}>{`curl -X POST ${window.location.origin}/api/v1/generate \\
  -H "X-API-Key: ${newKey}" \\
  -H "Content-Type: application/json" \\
  -d '{"prompt": "Write a business plan", "module": "auto"}'`}</pre>
          </div>
        )}

        <div className={styles.list}>
          {keys.length === 0 && <p className={styles.empty}>No API keys yet.</p>}
          {keys.map((k) => (
            <div key={k.id} className={styles.keyRow}>
              <div>
                <span className={styles.keyName}>{k.name}</span>
                <code className={styles.keyMasked}>{k.key}</code>
                <span className={styles.keyMeta}>{k.request_count} requests · {k.last_used ? `Last used ${new Date(k.last_used).toLocaleDateString()}` : "Never used"}</span>
              </div>
              <button className={styles.deleteBtn} onClick={() => deleteKey(k.id)}>Delete</button>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
