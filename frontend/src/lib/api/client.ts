import { useAuthStore } from "../../store/authStore";
import type { TokenResponse } from "../types";

const BASE = "/api/v1";

export class ApiError extends Error {
  status: number;
  data: unknown;
  constructor(status: number, message: string, data?: unknown) {
    super(message);
    this.name = "ApiError";
    this.status = status;
    this.data = data;
  }
}

async function request(
  path: string,
  options: RequestInit,
  auth: boolean,
): Promise<Response> {
  const headers = new Headers(options.headers);
  if (options.body && !headers.has("Content-Type")) {
    headers.set("Content-Type", "application/json");
  }
  if (auth) {
    const token = useAuthStore.getState().accessToken;
    if (token) headers.set("Authorization", `Bearer ${token}`);
  }
  return fetch(BASE + path, { ...options, headers, credentials: "include" });
}

// Single-flight refresh so concurrent 401s trigger only one refresh call.
let refreshInFlight: Promise<boolean> | null = null;

async function attemptRefresh(): Promise<boolean> {
  if (!refreshInFlight) {
    refreshInFlight = (async () => {
      const res = await request("/auth/refresh", { method: "POST" }, false);
      if (!res.ok) {
        useAuthStore.getState().clear();
        return false;
      }
      const data = (await res.json()) as TokenResponse;
      useAuthStore.getState().setAuth(data.access_token, data.user);
      return true;
    })().finally(() => {
      refreshInFlight = null;
    });
  }
  return refreshInFlight;
}

function extractMessage(data: unknown, fallback: string): string {
  if (data && typeof data === "object") {
    const detail = (data as Record<string, unknown>).detail;
    if (typeof detail === "string") return detail;
    if (Array.isArray(detail) && detail[0] && typeof detail[0] === "object") {
      const msg = (detail[0] as Record<string, unknown>).msg;
      if (typeof msg === "string") return msg;
    }
    const message = (data as Record<string, unknown>).message;
    if (typeof message === "string") return message;
  }
  return fallback;
}

interface ApiOptions {
  auth?: boolean;
  retryOn401?: boolean;
}

export async function api<T = unknown>(
  path: string,
  options: RequestInit = {},
  { auth = true, retryOn401 = true }: ApiOptions = {},
): Promise<T> {
  let res = await request(path, options, auth);

  if (res.status === 401 && auth && retryOn401) {
    const refreshed = await attemptRefresh();
    if (refreshed) res = await request(path, options, auth);
  }

  if (!res.ok) {
    let data: unknown = null;
    try {
      data = await res.json();
    } catch {
      /* non-JSON error body */
    }
    throw new ApiError(res.status, extractMessage(data, res.statusText), data);
  }

  if (res.status === 204) return undefined as T;
  return (await res.json()) as T;
}
