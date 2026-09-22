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

// ── cases & investigation engine ──
export interface CaseSummary {
  code: string;
  title: string;
  difficulty: number;
  org: string;
  summary: string;
  learning_objectives: string[];
  initial_clues: number;
}

export interface EntityView {
  ext_id: string;
  type: string;
  label: string;
  attributes: Record<string, unknown>;
  via: string | null;
}

export interface EvidenceView {
  ext_id: string;
  kind: string;
  source: string;
  reliability: "high" | "medium" | "low";
  content: string;
  related: string[];
  collected: boolean;
  note: string | null;
  tag: string | null;
}

export interface CaseBrief {
  code: string;
  title: string;
  difficulty: number;
  org: string;
  summary: string;
  learning_objectives: string[];
  initial_evidence_package: {
    entities: EntityView[];
    evidence: EvidenceView[];
  };
}

export interface EdgeView {
  id: string;
  source: string;
  target: string;
  rel_type: string;
}

export interface InvestigationState {
  investigation: { id: string; status: string; started_at: string };
  case: {
    code: string;
    title: string;
    difficulty: number;
    org: string;
    summary: string;
    learning_objectives: string[];
  };
  tools: string[];
  entities: EntityView[];
  evidence: EvidenceView[];
  edges: EdgeView[];
  counts: {
    entities_discovered: number;
    evidence_discovered: number;
    evidence_collected: number;
    relationships_drawn: number;
  };
}

export interface StartResult {
  investigation_id: string;
  resumed: boolean;
  state: InvestigationState;
}

export interface LookupResult {
  tool: string;
  query: string;
  hit: boolean;
  message: string;
  revealed: { entities: EntityView[]; evidence: EvidenceView[] };
}

export interface Debrief {
  verdict: {
    correct_actor: boolean;
    correct_vector: boolean;
    required_collected: string[];
    required_total: number;
    red_herrings_collected: string[];
    entities_discovered: number;
    evidence_collected: number;
  };
  solution: {
    actor_ext_id: string;
    actor_label: string | null;
    attack_vector: string;
    required_evidence: string[];
    red_herring_evidence: string[];
  };
  message: string;
  note: string;
}
