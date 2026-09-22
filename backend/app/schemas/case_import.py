"""The case authoring contract.

A case JSON is parsed into ``CaseIn``. Structural rules are enforced by field
types; cross-references and solvability are enforced by validators. Invalid
content fails here, at author/import time — never at play time.
"""
from __future__ import annotations

from pydantic import BaseModel, Field, model_validator

ENTITY_TYPES = {
    "username",
    "email",
    "domain",
    "ip",
    "person",
    "file",
    "social",
    "image",
    "device",
    "org",
}
TOOLS = {"search", "email", "domain", "ip", "identity", "image", "file"}
RELIABILITIES = {"high", "medium", "low"}


class EntityIn(BaseModel):
    ext_id: str
    type: str
    label: str
    attributes: dict = Field(default_factory=dict)
    initial: bool = False
    red_herring: bool = False

    @model_validator(mode="after")
    def _check_type(self) -> "EntityIn":
        if self.type not in ENTITY_TYPES:
            raise ValueError(f"entity '{self.ext_id}': unknown type '{self.type}'")
        return self


class RelationshipIn(BaseModel):
    ext_id: str
    source: str
    target: str
    rel_type: str
    correct: bool = True
    discoverable: bool = True


class EvidenceIn(BaseModel):
    ext_id: str
    kind: str
    source: str = ""
    reliability: str = "medium"
    content: str = ""
    relevance: int = Field(default=1, ge=0, le=5)
    related: list[str] = Field(default_factory=list)
    supports_solution: bool = False
    initial: bool = False

    @model_validator(mode="after")
    def _check_reliability(self) -> "EvidenceIn":
        if self.reliability not in RELIABILITIES:
            raise ValueError(f"evidence '{self.ext_id}': bad reliability '{self.reliability}'")
        return self


class OsintRevealsIn(BaseModel):
    entities: list[str] = Field(default_factory=list)
    evidence: list[str] = Field(default_factory=list)
    relationships: list[str] = Field(default_factory=list)


class OsintRecordIn(BaseModel):
    tool: str
    query: str
    reveals: OsintRevealsIn = Field(default_factory=OsintRevealsIn)
    response: str = ""

    @model_validator(mode="after")
    def _check_tool(self) -> "OsintRecordIn":
        if self.tool not in TOOLS:
            raise ValueError(f"osint record: unknown tool '{self.tool}'")
        return self


class TimelineIn(BaseModel):
    ext_id: str
    at: str
    label: str
    actor: str | None = None
    order: int = 0
    source: str | None = None
    discoverable: bool = True


class HintIn(BaseModel):
    level: int = Field(ge=1)
    body: str
    cost: int = Field(default=0, ge=0)


class SolutionIn(BaseModel):
    actor: str
    attack_vector: str
    required_evidence: list[str] = Field(default_factory=list)
    red_herring_evidence: list[str] = Field(default_factory=list)
    canonical_timeline: list[str] = Field(default_factory=list)
    weights: dict[str, int] = Field(default_factory=dict)


class CaseIn(BaseModel):
    code: str
    title: str
    difficulty: int = Field(ge=1, le=5)
    org: str = ""
    summary: str = ""
    learning_objectives: list[str] = Field(default_factory=list)
    entities: list[EntityIn]
    relationships: list[RelationshipIn] = Field(default_factory=list)
    evidence: list[EvidenceIn] = Field(default_factory=list)
    osint_records: list[OsintRecordIn] = Field(default_factory=list)
    timeline: list[TimelineIn] = Field(default_factory=list)
    hints: list[HintIn] = Field(default_factory=list)
    solution: SolutionIn

    # ── referential integrity + solvability ──────────────────────────────────
    @model_validator(mode="after")
    def _validate_graph(self) -> "CaseIn":
        entity_ids = _unique_ids([e.ext_id for e in self.entities], "entity")
        evidence_ids = _unique_ids([e.ext_id for e in self.evidence], "evidence")
        _unique_ids([r.ext_id for r in self.relationships], "relationship")
        _unique_ids([t.ext_id for t in self.timeline], "timeline event")

        if not any(e.initial for e in self.entities):
            raise ValueError("case must define at least one initial entity")

        # relationships reference real entities
        for r in self.relationships:
            for side in (r.source, r.target):
                if side not in entity_ids:
                    raise ValueError(f"relationship '{r.ext_id}' references unknown entity '{side}'")

        # evidence.related reference real entities
        for ev in self.evidence:
            for ent in ev.related:
                if ent not in entity_ids:
                    raise ValueError(f"evidence '{ev.ext_id}' references unknown entity '{ent}'")

        # osint reveals reference real ids
        rel_ids = {r.ext_id for r in self.relationships}
        for rec in self.osint_records:
            for ent in rec.reveals.entities:
                if ent not in entity_ids:
                    raise ValueError(f"osint '{rec.tool}:{rec.query}' reveals unknown entity '{ent}'")
            for ev in rec.reveals.evidence:
                if ev not in evidence_ids:
                    raise ValueError(f"osint '{rec.tool}:{rec.query}' reveals unknown evidence '{ev}'")
            for rl in rec.reveals.relationships:
                if rl not in rel_ids:
                    raise ValueError(f"osint '{rec.tool}:{rec.query}' reveals unknown relationship '{rl}'")

        # timeline actors reference real entities
        for t in self.timeline:
            if t.actor is not None and t.actor not in entity_ids:
                raise ValueError(f"timeline '{t.ext_id}' references unknown actor '{t.actor}'")

        # solution references
        sol = self.solution
        if sol.actor not in entity_ids:
            raise ValueError(f"solution actor '{sol.actor}' is not a defined entity")
        for ev in sol.required_evidence + sol.red_herring_evidence:
            if ev not in evidence_ids:
                raise ValueError(f"solution references unknown evidence '{ev}'")
        timeline_ids = {t.ext_id for t in self.timeline}
        for tid in sol.canonical_timeline:
            if tid not in timeline_ids:
                raise ValueError(f"solution canonical_timeline references unknown event '{tid}'")

        _check_reachability(self)
        return self


def _unique_ids(ids: list[str], kind: str) -> set[str]:
    seen: set[str] = set()
    for i in ids:
        if i in seen:
            raise ValueError(f"duplicate {kind} ext_id '{i}'")
        seen.add(i)
    return seen


def _check_reachability(case: "CaseIn") -> None:
    """Every entity must be discoverable from the initial clues, otherwise the
    case is unsolvable. This mirrors runtime discovery exactly: an OSINT record
    'unlocks' once an entity whose label matches its query has been discovered,
    and reveals its listed entities. (Players infer and draw relationships
    themselves — relationships do not auto-discover entities.)"""
    by_id = {e.ext_id: e for e in case.entities}

    reachable = {e.ext_id for e in case.entities if e.initial}
    changed = True
    while changed:
        changed = False
        reachable_labels = {by_id[i].label.strip().lower() for i in reachable}
        for rec in case.osint_records:
            if rec.query.strip().lower() in reachable_labels:
                for ent in rec.reveals.entities:
                    if ent not in reachable:
                        reachable.add(ent)
                        changed = True

    unreachable = [e.ext_id for e in case.entities if e.ext_id not in reachable]
    if unreachable:
        raise ValueError(
            "unreachable entities (case would be unsolvable): " + ", ".join(sorted(unreachable))
        )
