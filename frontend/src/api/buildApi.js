const API_BASE = import.meta.env.VITE_API_URL || "";

/**
 * Unified build request — routes to the correct AI module automatically.
 *
 * @param {string} prompt  - The user's prompt.
 * @param {string} module  - "auto" (default) or a specific module key:
 *                           "document" | "presentation" | "excel" |
 *                           "business" | "research" | "analytics" |
 *                           "content"  | "course"   | "court"     |
 *                           "professor"| "teacher"  | "exam"      |
 *                           "simulation"| "student" | "admin"     |
 *                           "multilingual" | "integrity"
 * @returns {Promise<object>} Normalised result compatible with PreviewPanel.
 */
export async function buildRequest(prompt, module = "auto") {
  const res = await fetch(`${API_BASE}/api/build`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ prompt, module }),
  });

  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail || "Build failed");
  }

  const data = await res.json();
  if (!data.success) throw new Error(data.error || "Build failed");
  return data;
}

/**
 * Upload a file and get an AI-generated summary.
 */
export async function uploadFile(file, module = "upload") {
  const formData = new FormData();
  formData.append("file", file);
  formData.append("module", module);

  const res = await fetch(`${API_BASE}/api/upload`, {
    method: "POST",
    body: formData,
  });

  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail || "Upload failed");
  }

  const data = await res.json();
  if (!data.success) throw new Error(data.error || "Upload failed");
  return data;
}

/**
 * Fetch all available templates from the backend.
 */
export async function fetchTemplates(module = "") {
  const url = module
    ? `${API_BASE}/api/templates?module=${encodeURIComponent(module)}`
    : `${API_BASE}/api/templates`;
  const res = await fetch(url);
  if (!res.ok) return [];
  return res.json();
}

/**
 * Detect which module would handle a prompt (no generation).
 */
export async function detectModule(prompt) {
  const res = await fetch(`${API_BASE}/api/detect-module`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ prompt }),
  });
  if (!res.ok) return { module: "document", module_name: "Documents AI" };
  return res.json();
}
