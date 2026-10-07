import hashlib
import json
from datetime import datetime, timezone
from urllib.request import Request, urlopen

from app.core.paths import (
    MANIFESTS_DATA_DIR,
    PROJECT_ROOT,
    RAW_DATA_DIR,
    SOURCES_MANIFEST_PATH,
)
from app.schemas.source import SourceDocument


USER_AGENT = (
    "FireSense/0.1 "
    "(reduced-gravity fire research prototype)"
)


def calculate_sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def load_source_manifest() -> dict:
    MANIFESTS_DATA_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    if not SOURCES_MANIFEST_PATH.exists():
        return {
            "version": "0.1.0",
            "sources": [],
        }

    content = (
        SOURCES_MANIFEST_PATH
        .read_text(encoding="utf-8")
        .strip()
    )

    if not content:
        return {
            "version": "0.1.0",
            "sources": [],
        }

    return json.loads(content)


def save_source_manifest(manifest: dict) -> None:
    MANIFESTS_DATA_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    temporary_path = (
        SOURCES_MANIFEST_PATH.with_suffix(".tmp")
    )

    temporary_path.write_text(
        json.dumps(
            manifest,
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    temporary_path.replace(
        SOURCES_MANIFEST_PATH
    )


def download_pdf(url: str) -> tuple[bytes, str]:
    request = Request(
        url,
        headers={
            "User-Agent": USER_AGENT,
        },
    )

    with urlopen(
        request,
        timeout=120,
    ) as response:
        data = response.read()

        content_type = (
            response.headers
            .get_content_type()
        )

    if not data.startswith(b"%PDF"):
        raise ValueError(
            "Downloaded content does not appear "
            "to be a valid PDF."
        )

    return data, content_type


def source_exists(
    manifest: dict,
    source_id: str,
) -> bool:
    return any(
        item.get("source_id") == source_id
        for item in manifest["sources"]
    )


def hash_exists(
    manifest: dict,
    sha256: str,
) -> bool:
    return any(
        item.get("sha256") == sha256
        for item in manifest["sources"]
    )


def ingest_pdf_source(
    source: SourceDocument,
) -> SourceDocument:
    if source.download_url is None:
        raise ValueError(
            "download_url is required "
            "for PDF ingestion."
        )

    manifest = load_source_manifest()

    if source_exists(
        manifest,
        source.source_id,
    ):
        raise ValueError(
            f"Source '{source.source_id}' "
            "already exists in the manifest."
        )

    print(
        f"Downloading: {source.title}"
    )

    pdf_data, content_type = download_pdf(
        str(source.download_url)
    )

    sha256 = calculate_sha256(pdf_data)

    if hash_exists(
        manifest,
        sha256,
    ):
        raise ValueError(
            "This exact PDF already exists "
            "in the FireSense corpus."
        )

    RAW_DATA_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    filename = f"{source.source_id}.pdf"

    destination = (
        RAW_DATA_DIR / filename
    )

    destination.write_bytes(pdf_data)

    relative_path = (
        destination
        .relative_to(PROJECT_ROOT)
        .as_posix()
    )

    completed_source = source.model_copy(
        update={
            "local_path": relative_path,
            "sha256": sha256,
            "file_size_bytes": len(pdf_data),
            "mime_type": content_type,
            "retrieved_at": datetime.now(
                timezone.utc
            ),
            "parser_status": "downloaded",
        }
    )

    manifest["sources"].append(
        completed_source.model_dump(
            mode="json"
        )
    )

    save_source_manifest(manifest)

    return completed_source