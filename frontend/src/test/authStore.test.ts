import { beforeEach, describe, expect, it } from "vitest";
import type { UserPublic } from "../lib/types";
import { useAuthStore } from "../store/authStore";

const sampleUser: UserPublic = {
  id: "11111111-1111-1111-1111-111111111111",
  email: "sleuth@aurelia.example",
  display_name: "Sleuth",
  role: "PLAYER",
  xp: 0,
  rank_level: 0,
  created_at: "2026-09-17T00:00:00Z",
};

describe("authStore", () => {
  beforeEach(() => {
    useAuthStore.setState({ status: "loading", accessToken: null, user: null });
  });

  it("marks the session authenticated on setAuth", () => {
    useAuthStore.getState().setAuth("access-token", sampleUser);
    const state = useAuthStore.getState();
    expect(state.status).toBe("authenticated");
    expect(state.accessToken).toBe("access-token");
    expect(state.user?.email).toBe("sleuth@aurelia.example");
  });

  it("returns to guest and drops the token on clear", () => {
    useAuthStore.getState().setAuth("access-token", sampleUser);
    useAuthStore.getState().clear();
    const state = useAuthStore.getState();
    expect(state.status).toBe("guest");
    expect(state.accessToken).toBeNull();
    expect(state.user).toBeNull();
  });
});
