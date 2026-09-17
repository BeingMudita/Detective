export type UserRole = "PLAYER" | "ADMIN";

export interface UserPublic {
  id: string;
  email: string;
  display_name: string;
  role: UserRole;
  xp: number;
  rank_level: number;
  created_at: string;
}

export interface TokenResponse {
  access_token: string;
  token_type: string;
  expires_in: number;
  user: UserPublic;
}
