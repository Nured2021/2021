const API_BASE = import.meta.env.VITE_API_URL || "";

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

export async function uploadMaterial(file, module = "student") {
  const formData = new FormData();
  formData.append("file", file);
  const res = await fetch(
    `${API_BASE}/education/upload-material?module=${encodeURIComponent(module)}`,
    { method: "POST", body: formData }
  );
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail || "Upload failed");
  }
  return res.json();
}

export async function educationChat({ message, module }) {
  const res = await fetch(`${API_BASE}/education/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ message, module: module || null }),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail || "Chat failed");
  }
  return res.json(); // { module, reply, history }
}

export async function fetchMaterials() {
  const res = await fetch(`${API_BASE}/education/materials`);
  if (!res.ok) throw new Error("Could not load materials");
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
