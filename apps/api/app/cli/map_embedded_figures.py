import json
import re
from pathlib import Path
from typing import Any

import pymupdf

from app.core.paths import (
    FIGURES_DATA_DIR,
    RAW_DATA_DIR,
)


SOURCE_ID = "SRC-NASA-20210011385"

TARGET_PAGES = (
    31,
    32,
    47,
    48,
    49,
)


FIGURE_PATTERN = re.compile(
    r"Figure\s+(\d+\.\d+)",
    re.IGNORECASE,
)


def horizontal_overlap_ratio(
    box_a: tuple[float, float, float, float],
    box_b: tuple[float, float, float, float],
) -> float:
    ax0, _, ax1, _ = box_a
    bx0, _, bx1, _ = box_b

    overlap = max(
        0.0,
        min(ax1, bx1) - max(ax0, bx0),
    )

    image_width = max(
        ax1 - ax0,
        1.0,
    )

    return overlap / image_width


def caption_score(
    image_bbox: tuple[float, float, float, float],
    caption_bbox: tuple[float, float, float, float],
) -> tuple[float, float, str]:

    _, iy0, _, iy1 = image_bbox
    _, cy0, _, cy1 = caption_bbox

    overlap = horizontal_overlap_ratio(
        image_bbox,
        caption_bbox,
    )

    # Captions are normally below figures.
    if cy0 >= iy1:
        vertical_gap = cy0 - iy1
        direction = "below"
        direction_penalty = 0.0

    elif cy1 <= iy0:
        vertical_gap = iy0 - cy1
        direction = "above"

        # Above-caption matches are possible,
        # but less likely.
        direction_penalty = 40.0

    else:
        vertical_gap = 0.0
        direction = "overlap"
        direction_penalty = 20.0

    horizontal_penalty = (
        50.0 * (1.0 - overlap)
    )

    score = (
        vertical_gap
        + direction_penalty
        + horizontal_penalty
    )

    return (
        score,
        vertical_gap,
        direction,
    )


def confidence_from_score(
    score: float,
    direction: str,
) -> str:

    if (
        score <= 45
        and direction == "below"
    ):
        return "high"

    if score <= 100:
        return "medium"

    return "low"


def get_caption_candidates(
    page: pymupdf.Page,
) -> list[dict[str, Any]]:

    candidates = []

    blocks = page.get_text(
        "dict"
    ).get(
        "blocks",
        []
    )

    for block in blocks:

        if block.get("type") != 0:
            continue

        lines = block.get(
            "lines",
            [],
        )

        text_parts = []

        for line in lines:
            for span in line.get(
                "spans",
                [],
            ):
                text_parts.append(
                    span.get(
                        "text",
                        "",
                    )
                )

        text = " ".join(
            text_parts
        ).strip()

        if not text:
            continue

        matches = list(
            FIGURE_PATTERN.finditer(
                text
            )
        )

        for match in matches:

            bbox = tuple(
                block.get(
                    "bbox",
                    (0, 0, 0, 0),
                )
            )

            candidates.append(
                {
                    "figure_ref": match.group(1),
                    "caption": text,
                    "bbox": bbox,
                }
            )

    return candidates


def map_page_images(
    page: pymupdf.Page,
    page_number: int,
    embedded_dir: Path,
) -> list[dict[str, Any]]:

    blocks = page.get_text(
        "dict"
    ).get(
        "blocks",
        []
    )

    captions = get_caption_candidates(
        page
    )

    mappings = []

    image_number = 0

    for block in blocks:

        if block.get("type") != 1:
            continue

        image_data = block.get(
            "image"
        )

        if not image_data:
            continue

        image_number += 1

        extension = block.get(
            "ext",
            "png",
        )

        filename = (
            f"page_{page_number:03d}"
            f"_image_{image_number:02d}"
            f".{extension}"
        )

        image_bbox = tuple(
            block.get(
                "bbox",
                (0, 0, 0, 0),
            )
        )

        ranked = []

        for caption in captions:

            score, gap, direction = (
                caption_score(
                    image_bbox,
                    caption["bbox"],
                )
            )

            ranked.append(
                {
                    **caption,
                    "score": round(
                        score,
                        2,
                    ),
                    "vertical_gap": round(
                        gap,
                        2,
                    ),
                    "direction": direction,
                }
            )

        ranked.sort(
            key=lambda item: (
                item["score"]
            )
        )

        best = (
            ranked[0]
            if ranked
            else None
        )

        if best is None:

            mappings.append(
                {
                    "page": page_number,
                    "image_file": filename,
                    "image_bbox": image_bbox,
                    "figure_ref": None,
                    "caption": None,
                    "confidence": "unresolved",
                    "score": None,
                    "candidate_captions": [],
                }
            )

            continue

        confidence = (
            confidence_from_score(
                best["score"],
                best["direction"],
            )
        )

        mappings.append(
            {
                "page": page_number,
                "image_file": filename,
                "image_path": str(
                    embedded_dir
                    / filename
                ),
                "image_bbox": image_bbox,
                "width": block.get(
                    "width"
                ),
                "height": block.get(
                    "height"
                ),
                "figure_ref": best[
                    "figure_ref"
                ],
                "caption": best[
                    "caption"
                ],
                "caption_bbox": best[
                    "bbox"
                ],
                "direction": best[
                    "direction"
                ],
                "vertical_gap": best[
                    "vertical_gap"
                ],
                "score": best[
                    "score"
                ],
                "confidence": confidence,
                "candidate_captions": (
                    ranked[:3]
                ),
            }
        )

    return mappings


def main():

    pdf_path = (
        RAW_DATA_DIR
        / f"{SOURCE_ID}.pdf"
    )

    embedded_dir = (
        FIGURES_DATA_DIR
        / SOURCE_ID
        / "embedded"
    )

    output_path = (
        FIGURES_DATA_DIR
        / SOURCE_ID
        / "figure_map.json"
    )

    document = pymupdf.open(
        pdf_path
    )

    mappings = []

    for page_number in TARGET_PAGES:

        page = document[
            page_number - 1
        ]

        mappings.extend(
            map_page_images(
                page=page,
                page_number=page_number,
                embedded_dir=embedded_dir,
            )
        )

    document.close()

    # Group raster parts belonging
    # to the same figure.
    figure_groups = {}

    for item in mappings:

        figure_ref = item[
            "figure_ref"
        ]

        if figure_ref is None:
            continue

        figure_groups.setdefault(
            figure_ref,
            [],
        ).append(
            item["image_file"]
        )

    output = {
        "source_id": SOURCE_ID,
        "mapping_count": len(
            mappings
        ),
        "figure_groups": (
            figure_groups
        ),
        "mappings": mappings,
    }

    output_path.write_text(
        json.dumps(
            output,
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    print()
    print(
        "EMBEDDED IMAGE → FIGURE MAP"
    )
    print(
        "---------------------------"
    )

    for item in mappings:

        print()

        print(
            item["image_file"]
        )

        print(
            "  page       :",
            item["page"],
        )

        print(
            "  figure     :",
            item["figure_ref"],
        )

        print(
            "  confidence :",
            item["confidence"],
        )

        print(
            "  score      :",
            item["score"],
        )

        if item["caption"]:

            print(
                "  caption    :",
                item["caption"][:180],
            )

    print()
    print(
        "FIGURE GROUPS"
    )
    print(
        "-------------"
    )

    for figure_ref, files in (
        figure_groups.items()
    ):

        print(
            f"Figure {figure_ref}:"
        )

        for filename in files:
            print(
                f"  - {filename}"
            )

    print()
    print(
        f"Saved: {output_path}"
    )


if __name__ == "__main__":
    main()