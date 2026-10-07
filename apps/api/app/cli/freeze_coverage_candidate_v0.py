import hashlib
import json
from pathlib import Path

from app.core.paths import CURATED_DATA_DIR
from app.services.next_experiment_candidate import (
    NextExperimentCandidateBuilder,
)


def sha256_file(path: Path) -> str:
    hasher = hashlib.sha256()

    with path.open("rb") as file:
        for chunk in iter(
            lambda: file.read(1024 * 1024),
            b"",
        ):
            hasher.update(chunk)

    return hasher.hexdigest()


def main() -> None:
    thin_sheet_dir = (
        CURATED_DATA_DIR
        / "thin_sheet"
    )

    gap_map_path = (
        thin_sheet_dir
        / "evidence_gap_map_v0.json"
    )

    output_dir = (
        thin_sheet_dir
        / "models"
    )

    output_path = (
        output_dir
        / "coverage_next_experiment_candidate_v0.json"
    )

    if not gap_map_path.exists():
        raise FileNotFoundError(
            f"Missing evidence gap map: {gap_map_path}"
        )

    gap_map = json.loads(
        gap_map_path.read_text(
            encoding="utf-8"
        )
    )

    builder = (
        NextExperimentCandidateBuilder(
            gap_map_path=gap_map_path
        )
    )

    candidate = (
        builder.build()
    )

    artifact = {
        "artifact_name": (
            "FireSense Coverage "
            "Next Experiment Candidate v0"
        ),

        "artifact_version": "v0",

        "source_id": (
            gap_map["source_id"]
        ),

        "dataset_version": (
            gap_map["dataset_version"]
        ),

        "dataset_sha256": (
            gap_map["dataset_sha256"]
        ),

        "canonical_evidence_figure": (
            gap_map[
                "canonical_evidence_figure"
            ]
        ),

        "source_gap_map": (
            "evidence_gap_map_v0.json"
        ),

        "source_gap_map_sha256": (
            sha256_file(
                gap_map_path
            )
        ),

        "candidate": (
            candidate.model_dump(
                mode="json"
            )
        ),

        "status": (
            "coverage_candidate_frozen"
        ),
    }

    output_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    output_path.write_text(
        json.dumps(
            artifact,
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    matched_pair = (
        artifact[
            "candidate"
        ][
            "matched_pair"
        ]
    )

    print()
    print(
        "FIRESENSE COVERAGE "
        "CANDIDATE V0"
    )

    print(
        "------------------------------"
    )

    print(
        "Candidate ID:"
    )

    print(
        " ",
        artifact[
            "candidate"
        ][
            "candidate_id"
        ],
    )

    print()
    print(
        "Microgravity candidate:"
    )

    print(
        f"  "
        f"{matched_pair['microgravity_thickness_um']:.6f} um"
    )

    print()
    print(
        "Normal-gravity candidate:"
    )

    print(
        f"  "
        f"{matched_pair['normal_gravity_thickness_um']:.6f} um"
    )

    print()
    print(
        "Matched-pair thickness:"
    )

    print(
        f"  "
        f"{matched_pair['thickness_um']:.6f} um"
    )

    print()
    print(
        "Relative difference:"
    )

    print(
        f"  "
        f"{matched_pair['relative_difference'] * 100:.4f}%"
    )

    print()
    print(
        "Recommendation:"
    )

    print(
        "  COVERAGE CANDIDATE ONLY"
    )

    print(
        "  NOT APPROVED"
    )

    print()
    print(
        "Saved:"
    )

    print(
        f"  {output_path}"
    )


if __name__ == "__main__":
    main()