import type {
  Debrief,
  EdgeView,
  EvidenceView,
  InvestigationState,
  LookupResult,
} from "../types";
import { api } from "./client";

const base = (id: string) => `/investigations/${encodeURIComponent(id)}`;

export function getInvestigation(id: string) {
  return api<InvestigationState>(base(id));
}

export function runLookup(id: string, tool: string, query: string) {
  return api<LookupResult>(`${base(id)}/lookup`, {
    method: "POST",
    body: JSON.stringify({ tool, query }),
  });
}

export function collectEvidence(
  id: string,
  evidenceExtId: string,
  tag?: string,
  note?: string,
) {
  return api<EvidenceView>(`${base(id)}/evidence`, {
    method: "POST",
    body: JSON.stringify({ evidence_ext_id: evidenceExtId, tag, note }),
  });
}

export function addEdge(id: string, source: string, target: string, relType = "linked") {
  return api<EdgeView>(`${base(id)}/edges`, {
    method: "POST",
    body: JSON.stringify({ source, target, rel_type: relType }),
  });
}

export function submitCase(
  id: string,
  actorExtId: string,
  attackVector: string,
  citedEvidence: string[],
  summary: string,
) {
  return api<Debrief>(`${base(id)}/submit`, {
    method: "POST",
    body: JSON.stringify({
      actor_ext_id: actorExtId,
      attack_vector: attackVector,
      cited_evidence: citedEvidence,
      summary,
    }),
  });
}

export function getAttackVectors() {
  return api<{ attack_vectors: string[] }>("/meta/attack-vectors");
}
