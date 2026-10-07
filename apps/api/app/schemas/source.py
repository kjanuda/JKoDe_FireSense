from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field, HttpUrl, field_validator


class SourceDocument(BaseModel):
    source_id: str

    external_id: str | None = None

    title: str

    source_type: Literal[
        "ntrs_report",
        "journal_article",
        "conference_paper",
        "psi_dataset",
        "nasa_standard",
        "technical_memorandum",
        "other",
    ]

    organization: str | None = None

    authors: list[str] = Field(default_factory=list)

    publication_year: int | None = Field(
        default=None,
        ge=1900,
        le=2100,
    )

    # Human-facing source record
    canonical_url: HttpUrl | None = None

    # Direct downloadable PDF/data URL
    download_url: HttpUrl | None = None

    # Local provenance
    local_path: str | None = None

    sha256: str | None = None

    file_size_bytes: int | None = Field(
        default=None,
        ge=0,
    )

    mime_type: str | None = None

    retrieved_at: datetime | None = None

    parser_status: Literal[
        "not_downloaded",
        "downloaded",
        "parsing",
        "parsed",
        "failed",
    ] = "not_downloaded"

    notes: str | None = None

    @field_validator("sha256")
    @classmethod
    def validate_sha256(cls, value: str | None):
        if value is None:
            return value

        cleaned = value.lower()

        if len(cleaned) != 64:
            raise ValueError(
                "sha256 must contain exactly 64 hexadecimal characters"
            )

        allowed = set("0123456789abcdef")

        if any(char not in allowed for char in cleaned):
            raise ValueError(
                "sha256 must contain only hexadecimal characters"
            )

        return cleaned