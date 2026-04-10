const API_BASE = import.meta.env.VITE_API_URL || "";

export async function generateDocument({ prompt, docType }) {
  const res = await fetch(`${API_BASE}/generate-document`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ prompt, doc_type: docType }),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail || "Request failed");
  }
  return res.json();
}

export function downloadUrl(relPath) {
  return `${API_BASE}${relPath}`;
}
