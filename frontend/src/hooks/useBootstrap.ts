import { useEffect } from "react";
import { refreshSession } from "../lib/api/auth";
import { useAuthStore } from "../store/authStore";

/**
 * On first load, try to restore a session from the httpOnly refresh cookie.
 * Success -> authenticated; failure -> guest. Runs exactly once.
 */
export function useBootstrap() {
  useEffect(() => {
    let cancelled = false;
    (async () => {
      try {
        const session = await refreshSession();
        if (!cancelled) {
          useAuthStore.getState().setAuth(session.access_token, session.user);
        }
      } catch {
        if (!cancelled) useAuthStore.getState().clear();
      }
    })();
    return () => {
      cancelled = true;
    };
  }, []);
}
