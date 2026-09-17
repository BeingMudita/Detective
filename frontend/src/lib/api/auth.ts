import type { TokenResponse, UserPublic } from "../types";
import { api } from "./client";

export function login(email: string, password: string) {
  return api<TokenResponse>(
    "/auth/login",
    { method: "POST", body: JSON.stringify({ email, password }) },
    { auth: false },
  );
}

export function register(email: string, password: string, displayName?: string) {
  return api<TokenResponse>(
    "/auth/register",
    {
      method: "POST",
      body: JSON.stringify({ email, password, display_name: displayName }),
    },
    { auth: false },
  );
}

export function logout() {
  return api<{ message: string }>(
    "/auth/logout",
    { method: "POST" },
    { auth: false },
  );
}

export function refreshSession() {
  return api<TokenResponse>(
    "/auth/refresh",
    { method: "POST" },
    { auth: false, retryOn401: false },
  );
}

export function fetchMe() {
  return api<UserPublic>("/me");
}
