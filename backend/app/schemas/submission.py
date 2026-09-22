from __future__ import annotations

from pydantic import BaseModel, Field

# Fixed set offered to the player at submission time.
ATTACK_VECTORS = [
    "compromised_credentials",
    "phishing",
    "insider_threat",
    "misconfiguration",
    "malware",
    "accidental_disclosure",
    "supply_chain",
]


class SubmitRequest(BaseModel):
    actor_ext_id: str = Field(min_length=1, max_length=64)
    attack_vector: str = Field(min_length=1, max_length=48)
    cited_evidence: list[str] = Field(default_factory=list)
    summary: str = Field(default="", max_length=2000)
