const API_BASE = import.meta.env.VITE_API_URL || "http://localhost:8000";

/**
 * Unified build request.
 *
 * @param {string} prompt  - The user's prompt.
 * @param {string} mode    - "auto" (default) or a specific type:
 *                           "document" | "presentation" | "spreadsheet" |
 *                           "education" | "research"
 * @returns {Promise<object>} Normalised result compatible with PreviewPanel.
 */
export async function buildRequest(prompt, mode = "auto") {
  const res = await fetch(`${API_BASE}/api/build`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ prompt, mode }),
  });

  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail || "Build failed");
  }

  const data = await res.json();

  if (!data.success) {
    throw new Error(data.error || "Build failed");
  }

  return data;
}
