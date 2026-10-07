import hashlib
import re
from typing import Any


def normalize_text(text: str) -> str:
    text = text.lower()

    text = re.sub(
        r"\s+",
        " ",
        text,
    )

    return text.strip()


def text_hash(text: str) -> str:
    normalized = normalize_text(text)

    return hashlib.sha256(
        normalized.encode("utf-8")
    ).hexdigest()


def deduplicate_candidates(
    candidates: list[dict[str, Any]],
) -> list[dict[str, Any]]:

    seen = set()

    result = []

    for candidate in candidates:

        text = candidate.get(
            "context",
            "",
        )

        fingerprint = text_hash(text)

        if fingerprint in seen:
            continue

        seen.add(fingerprint)

        result.append(
            {
                **candidate,
                "content_hash": fingerprint,
            }
        )

    return result