export const BASE = (import.meta.env.VITE_API_URL || "http://localhost:3000").replace(/\/$/, "");

async function call(path, opts) {
  const r = await fetch(BASE + path, opts);
  if (!r.ok) throw new Error(`API ${r.status}`);
  return r.json();
}

export const get = (path, params = {}) => {
  const q = new URLSearchParams(Object.entries(params).filter(([, v]) => v !== "" && v != null)).toString();
  return call(path + (q ? "?" + q : ""));
};

export const post = (path, body) =>
  call(path, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(body) });
