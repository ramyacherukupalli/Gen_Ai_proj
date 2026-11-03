const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "http://127.0.0.1:8000/api";

async function request(path, options = {}) {
  const response = await fetch(`${API_BASE_URL}${path}`, options);
  if (response.ok) return response;

  let detail = "Something went wrong. Please try again.";
  try {
    const body = await response.json();
    detail = body.detail ?? detail;
  } catch {
    // A non-JSON error response still receives a clear client-facing message.
  }
  throw new Error(detail);
}

export async function getModels() {
  return (await request("/models")).json();
}

export async function getOptions() {
  return (await request("/options")).json();
}

export async function generateNotes(payload) {
  return (await request("/notes/generate", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  })).json();
}

export async function downloadNotes(content, exportFormat) {
  const response = await request("/notes/export", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ content, export_format: exportFormat }),
  });
  const blob = await response.blob();
  const objectUrl = URL.createObjectURL(blob);
  const anchor = document.createElement("a");
  anchor.href = objectUrl;
  anchor.download = `ml-study-notes.${exportFormat === "pdf" ? "pdf" : "md"}`;
  document.body.appendChild(anchor);
  anchor.click();
  anchor.remove();
  URL.revokeObjectURL(objectUrl);
}
