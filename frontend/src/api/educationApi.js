const API_BASE = import.meta.env.VITE_API_URL || "http://localhost:8000";

export async function generateEducation({ prompt, module }) {
  const res = await fetch(`${API_BASE}/education/generate`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ prompt, module: module || null }),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail || "Request failed");
  }
  return res.json();
}

export async function fetchModules() {
  const res = await fetch(`${API_BASE}/education/modules`);
  if (!res.ok) throw new Error("Could not load education modules");
  return res.json();
}

export function downloadUrl(relPath) {
  return `${API_BASE}${relPath}`;
}
