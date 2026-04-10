import { useEffect, useRef, useState } from "react";
import styles from "./SearchBar.module.css";

const API_BASE = import.meta.env.VITE_API_URL || "";

export default function SearchBar({ onResult }) {
  const [query, setQuery]         = useState("");
  const [suggestions, setSugs]    = useState([]);
  const [results, setResults]     = useState(null);
  const [loading, setLoading]     = useState(false);
  const [open, setOpen]           = useState(false);
  const timerRef = useRef(null);
  const inputRef = useRef(null);

  // Autocomplete suggestions
  useEffect(() => {
    clearTimeout(timerRef.current);
    if (query.length < 2) { setSugs([]); return; }
    timerRef.current = setTimeout(async () => {
      try {
        const r = await fetch(`${API_BASE}/api/search/suggestions?q=${encodeURIComponent(query)}&limit=6`);
        const data = await r.json();
        setSugs(Array.isArray(data) ? data : []);
      } catch {}
    }, 250);
  }, [query]);

  const search = async (q = query) => {
    if (!q.trim()) return;
    setLoading(true);
    setSugs([]);
    setOpen(true);
    try {
      const r = await fetch(`${API_BASE}/api/search`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query: q.trim(), limit: 20 }),
      });
      const data = await r.json();
      setResults(data.results || []);
    } catch {
      setResults([]);
    } finally {
      setLoading(false);
    }
  };

  const handleKey = (e) => {
    if (e.key === "Enter") search();
    if (e.key === "Escape") { setOpen(false); setSugs([]); }
  };

  if (!open) {
    return (
      <div className={styles.collapsed}>
        <button className={styles.openBtn} onClick={() => { setOpen(true); setTimeout(() => inputRef.current?.focus(), 50); }}>
          🔍 Search
        </button>
      </div>
    );
  }

  return (
    <div className={styles.container}>
      <div className={styles.inputRow}>
        <input
          ref={inputRef}
          className={styles.input}
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          onKeyDown={handleKey}
          placeholder="Search across all documents…"
          autoFocus
        />
        <button className={styles.searchBtn} onClick={() => search()}>🔍</button>
        <button className={styles.closeBtn} onClick={() => { setOpen(false); setResults(null); setQuery(""); }}>✕</button>
      </div>

      {/* Autocomplete */}
      {suggestions.length > 0 && (
        <div className={styles.sugs}>
          {suggestions.map((s) => (
            <button key={s} className={styles.sugItem}
              onClick={() => { setQuery(s); search(s); }}>
              {s}
            </button>
          ))}
        </div>
      )}

      {/* Results */}
      {loading && <p className={styles.loading}>Searching…</p>}
      {!loading && results !== null && (
        <div className={styles.results}>
          {results.length === 0 ? (
            <p className={styles.noResults}>No results found for "{query}"</p>
          ) : (
            <>
              <p className={styles.count}>{results.length} result{results.length !== 1 ? "s" : ""}</p>
              {results.map((r) => (
                <div key={r.id} className={styles.resultItem}
                  onClick={() => { onResult?.(r); setOpen(false); }}>
                  <span className={styles.resultModule}>{r.module}</span>
                  <span className={styles.resultTitle}>{r.title}</span>
                  <p className={styles.resultPreview}>{r.preview}</p>
                </div>
              ))}
            </>
          )}
        </div>
      )}
    </div>
  );
}
