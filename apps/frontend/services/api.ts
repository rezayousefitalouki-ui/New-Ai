const API_BASE = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

function readCookie(name: string): string | undefined {
  if (typeof document === "undefined") return undefined;
  const item = document.cookie.split("; ").find((cookie) => cookie.startsWith(`${name}=`));
  return item ? decodeURIComponent(item.split("=").slice(1).join("=")) : undefined;
}

export async function apiRequest<T>(path: string, init: RequestInit = {}): Promise<T> {
  const method = (init.method ?? "GET").toUpperCase();
  const headers = new Headers(init.headers);
  if (init.body && !(init.body instanceof FormData) && !headers.has("Content-Type")) {
    headers.set("Content-Type", "application/json");
  }
  const csrfToken = readCookie("csrftoken");
  if (csrfToken && !["GET", "HEAD", "OPTIONS", "TRACE"].includes(method)) {
    headers.set("X-CSRFToken", csrfToken);
  }
  const response = await fetch(new URL(path, API_BASE), { ...init, method, credentials:"include", headers });
  if (!response.ok) {
    let message = `درخواست ناموفق بود (${response.status})`;
    try {
      const payload = await response.json();
      message = payload.detail ?? Object.values(payload).flat().join(" ");
    } catch {
      const detail = await response.text();
      if (detail) message = detail;
    }
    throw new Error(message);
  }
  if (response.status === 204) return undefined as T;
  return response.json() as Promise<T>;
}

export async function ensureCsrf(): Promise<void> {
  await apiRequest("/api/v1/auth/csrf/");
}
