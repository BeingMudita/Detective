import type { CaseBrief, CaseSummary, StartResult } from "../types";
import { api } from "./client";

export function listCases() {
  return api<CaseSummary[]>("/cases");
}

export function getCaseBrief(code: string) {
  return api<CaseBrief>(`/cases/${encodeURIComponent(code)}`);
}

export function startCase(code: string) {
  return api<StartResult>(`/cases/${encodeURIComponent(code)}/start`, {
    method: "POST",
  });
}
