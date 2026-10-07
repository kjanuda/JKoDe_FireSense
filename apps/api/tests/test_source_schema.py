import pytest
from pydantic import ValidationError

from app.schemas.source import SourceDocument


def test_valid_source_document():
    source = SourceDocument(
        source_id="SRC-NASA-001",
        title="Example NASA Reduced-Gravity Fire Study",
        source_type="ntrs_report",
        organization="NASA",
        authors=[
            "Researcher One",
            "Researcher Two",
        ],
        publication_year=2021,
        canonical_url="https://ntrs.nasa.gov/",
        local_path="data/raw/SRC-NASA-001.pdf",
        parser_status="downloaded",
    )

    assert source.source_id == "SRC-NASA-001"
    assert source.organization == "NASA"
    assert source.parser_status == "downloaded"


def test_valid_sha256():
    sha256 = "a" * 64

    source = SourceDocument(
        source_id="SRC-NASA-002",
        title="Example Source",
        source_type="technical_memorandum",
        sha256=sha256,
    )

    assert source.sha256 == sha256


def test_invalid_sha256_is_rejected():
    with pytest.raises(ValidationError):
        SourceDocument(
            source_id="SRC-NASA-003",
            title="Invalid Hash Example",
            source_type="journal_article",
            sha256="not-a-valid-sha256",
        )


def test_invalid_publication_year_is_rejected():
    with pytest.raises(ValidationError):
        SourceDocument(
            source_id="SRC-NASA-004",
            title="Invalid Year Example",
            source_type="conference_paper",
            publication_year=1800,
        )