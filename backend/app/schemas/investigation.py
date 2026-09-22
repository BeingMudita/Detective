from __future__ import annotations

from pydantic import BaseModel, Field


class LookupRequest(BaseModel):
    tool: str = Field(min_length=1, max_length=32)
    query: str = Field(min_length=1, max_length=200)


class CollectRequest(BaseModel):
    evidence_ext_id: str = Field(min_length=1, max_length=64)
    note: str | None = Field(default=None, max_length=500)
    tag: str | None = Field(default=None, max_length=48)


class EdgeRequest(BaseModel):
    source: str = Field(min_length=1, max_length=64)
    target: str = Field(min_length=1, max_length=64)
    rel_type: str | None = Field(default="linked", max_length=48)


class ActionRequest(BaseModel):
    action_type: str = Field(min_length=1, max_length=48)
    payload: dict = Field(default_factory=dict)
