from pydantic import (
    BaseModel,
    Field,
)


class ValidationSourceRegistryEntry(BaseModel):
    source_id: str
    title: str
    doi: str | None = None
    reference: str | None = None
    campaign: str
    independence_status: str
    current_role: str
    direct_validation_eligible: bool
    blocking_reasons: list[str]


class ValidationSourceRegistryResponse(BaseModel):
    registry_id: str
    version: str
    registry_sha256: str
    artifact_sha256_verified: bool
    firesense_training_source_ids: list[str]
    sources: list[
        ValidationSourceRegistryEntry
    ]
    guardrails: list[str]


class ValidationSourceCheckRequest(BaseModel):
    source_id: str = Field(
        min_length=1,
    )


class ValidationSourceCheckResponse(BaseModel):
    source_id: str
    known_source: bool
    independence_status: str
    current_role: str
    direct_validation_eligible: bool
    blocking_reasons: list[str]
    registry_sha256: str
    artifact_sha256_verified: bool
