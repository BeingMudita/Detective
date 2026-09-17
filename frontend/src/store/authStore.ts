import { create } from "zustand";
import type { UserPublic } from "../lib/types";

export type AuthStatus = "loading" | "authenticated" | "guest";

interface AuthState {
  status: AuthStatus;
  accessToken: string | null;
  user: UserPublic | null;
  setAuth: (accessToken: string, user: UserPublic) => void;
  setAccessToken: (accessToken: string) => void;
  clear: () => void;
}

export const useAuthStore = create<AuthState>((set) => ({
  status: "loading",
  accessToken: null,
  user: null,
  setAuth: (accessToken, user) =>
    set({ accessToken, user, status: "authenticated" }),
  setAccessToken: (accessToken) => set({ accessToken }),
  clear: () => set({ accessToken: null, user: null, status: "guest" }),
}));
