import hashlib
import json
import math
from pathlib import Path

from app.core.paths import CURATED_DATA_DIR


DATASET_PATH = (
    CURATED_DATA_DIR
    / "thin_sheet"
    / "baseline_dataset_v0.jsonl"
)

MANIFEST_PATH = (
    CURATED_DATA_DIR
    / "thin_sheet"
    / "baseline_dataset_v0_manifest.json"
)


SUPPORTED_GROUPS = (
    "microgravity",
    "normal_gravity",
)


EXPECTED_COUNTS = {
    "microgravity": 4,
    "normal_gravity": 9,
}


class EvidenceGapAnalyzer:

    def __init__(
        self,
        dataset_path: Path = DATASET_PATH,
        manifest_path: Path = MANIFEST_PATH,
    ) -> None:

        self.dataset_path = dataset_path
        self.manifest_path = manifest_path

        self.manifest = self._load_json(
            self.manifest_path
        )

        self.rows = self._load_jsonl(
            self.dataset_path
        )

        self.actual_sha256 = (
            self._sha256_file(
                self.dataset_path
            )
        )

        self._validate()

    @staticmethod
    def _load_json(
        path: Path,
    ) -> dict:

        if not path.exists():

            raise FileNotFoundError(
                f"Missing file: {path}"
            )

        return json.loads(
            path.read_text(
                encoding="utf-8"
            )
        )

    @staticmethod
    def _load_jsonl(
        path: Path,
    ) -> list[dict]:

        if not path.exists():

            raise FileNotFoundError(
                f"Missing file: {path}"
            )

        rows = []

        with path.open(
            "r",
            encoding="utf-8",
        ) as file:

            for line_number, raw_line in enumerate(
                file,
                start=1,
            ):

                line = raw_line.strip()

                if not line:
                    continue

                try:

                    rows.append(
                        json.loads(
                            line
                        )
                    )

                except json.JSONDecodeError as exc:

                    raise ValueError(
                        f"Invalid JSONL at "
                        f"line {line_number}: "
                        f"{exc}"
                    ) from exc

        return rows

    @staticmethod
    def _sha256_file(
        path: Path,
    ) -> str:

        digest = hashlib.sha256()

        with path.open(
            "rb"
        ) as file:

            while True:

                chunk = file.read(
                    1024 * 1024
                )

                if not chunk:
                    break

                digest.update(
                    chunk
                )

        return digest.hexdigest()

    def _validate(
        self,
    ) -> None:

        expected_sha = str(
            self.manifest[
                "dataset_sha256"
            ]
        )

        if (
            expected_sha
            != self.actual_sha256
        ):

            raise ValueError(
                "Baseline dataset SHA256 "
                "does not match manifest."
            )

        if len(
            self.rows
        ) != 13:

            raise ValueError(
                f"Expected 13 rows, "
                f"found {len(self.rows)}."
            )

        for row in self.rows:

            if (
                row.get(
                    "figure_ref"
                )
                != "2.21"
            ):

                raise ValueError(
                    "Gap map may only use "
                    "canonical Figure 2.21 "
                    "evidence."
                )

            gravity = row.get(
                "gravity_regime"
            )

            if (
                gravity
                not in SUPPORTED_GROUPS
            ):

                raise ValueError(
                    f"Unsupported gravity "
                    f"group: {gravity}"
                )

            thickness = float(
                row[
                    "thickness_um"
                ]
            )

            if thickness <= 0:

                raise ValueError(
                    "Thickness must be "
                    "positive."
                )

    def _rows_for_group(
        self,
        group_name: str,
    ) -> list[dict]:

        rows = [
            row
            for row in self.rows
            if (
                row[
                    "gravity_regime"
                ]
                == group_name
            )
        ]

        rows = sorted(
            rows,
            key=lambda row: float(
                row[
                    "thickness_um"
                ]
            ),
        )

        expected = (
            EXPECTED_COUNTS[
                group_name
            ]
        )

        if len(
            rows
        ) != expected:

            raise ValueError(
                f"{group_name}: "
                f"expected {expected}, "
                f"found {len(rows)}."
            )

        return rows

    @staticmethod
    def _build_intervals(
        rows: list[dict],
    ) -> list[dict]:

        intervals = []

        for index in range(
            len(rows) - 1
        ):

            left = rows[
                index
            ]

            right = rows[
                index + 1
            ]

            left_t = float(
                left[
                    "thickness_um"
                ]
            )

            right_t = float(
                right[
                    "thickness_um"
                ]
            )

            thickness_ratio = (
                right_t
                / left_t
            )

            log_gap_decades = (
                math.log10(
                    right_t
                )
                - math.log10(
                    left_t
                )
            )

            geometric_midpoint = (
                math.sqrt(
                    left_t
                    * right_t
                )
            )

            intervals.append(
                {
                    "left_record_id": (
                        left[
                            "record_id"
                        ]
                    ),

                    "right_record_id": (
                        right[
                            "record_id"
                        ]
                    ),

                    "left_thickness_um": (
                        left_t
                    ),

                    "right_thickness_um": (
                        right_t
                    ),

                    "thickness_ratio": (
                        thickness_ratio
                    ),

                    "log_gap_decades": (
                        log_gap_decades
                    ),

                    "coverage_candidate_thickness_um": (
                        geometric_midpoint
                    ),

                    "candidate_method": (
                        "geometric_midpoint_of_"
                        "adjacent_observed_"
                        "log_thickness_gap"
                    ),
                }
            )

        max_gap = max(
            interval[
                "log_gap_decades"
            ]
            for interval
            in intervals
        )

        for interval in intervals:

            interval[
                "relative_gap_score"
            ] = (
                interval[
                    "log_gap_decades"
                ]
                / max_gap
            )

        return intervals

    def build(
        self,
    ) -> dict:

        groups = {}

        all_intervals = []

        for group_name in (
            SUPPORTED_GROUPS
        ):

            rows = (
                self._rows_for_group(
                    group_name
                )
            )

            intervals = (
                self._build_intervals(
                    rows
                )
            )

            ranked_intervals = (
                sorted(
                    intervals,
                    key=lambda item: (
                        item[
                            "log_gap_decades"
                        ]
                    ),
                    reverse=True,
                )
            )

            largest_gap = (
                ranked_intervals[
                    0
                ]
            )

            observations = [
                {
                    "record_id": (
                        row[
                            "record_id"
                        ]
                    ),

                    "thickness_um": float(
                        row[
                            "thickness_um"
                        ]
                    ),

                    "spread_rate_mm_s": float(
                        row[
                            "spread_rate_mm_s"
                        ]
                    ),
                }
                for row in rows
            ]

            groups[
                group_name
            ] = {
                "record_count": (
                    len(rows)
                ),

                "empirical_domain_um": {
                    "min": float(
                        rows[
                            0
                        ][
                            "thickness_um"
                        ]
                    ),

                    "max": float(
                        rows[
                            -1
                        ][
                            "thickness_um"
                        ]
                    ),
                },

                "observations": (
                    observations
                ),

                "intervals": (
                    intervals
                ),

                "largest_internal_gap": (
                    largest_gap
                ),

                "coverage_candidate": {
                    "thickness_um": (
                        largest_gap[
                            "coverage_candidate_thickness_um"
                        ]
                    ),

                    "left_record_id": (
                        largest_gap[
                            "left_record_id"
                        ]
                    ),

                    "right_record_id": (
                        largest_gap[
                            "right_record_id"
                        ]
                    ),

                    "basis": (
                        "largest unsampled "
                        "internal interval in "
                        "log-thickness space"
                    ),

                    "status": (
                        "coverage_heuristic_only"
                    ),
                },
            }

            for interval in intervals:

                all_intervals.append(
                    {
                        "gravity_regime": (
                            group_name
                        ),

                        **interval,
                    }
                )

        global_ranking = sorted(
            all_intervals,
            key=lambda item: (
                item[
                    "log_gap_decades"
                ]
            ),
            reverse=True,
        )

        micro_candidate = float(
            groups[
                "microgravity"
            ][
                "coverage_candidate"
            ][
                "thickness_um"
            ]
        )

        normal_candidate = float(
            groups[
                "normal_gravity"
            ][
                "coverage_candidate"
            ][
                "thickness_um"
            ]
        )

        relative_difference = (
            abs(
                micro_candidate
                - normal_candidate
            )
            / (
                (
                    micro_candidate
                    + normal_candidate
                )
                / 2.0
            )
        )

        paired_candidate_possible = (
            relative_difference
            <= 0.10
        )

        return {
            "gap_map_name": (
                "FireSense PMMA "
                "Evidence Gap Map v0"
            ),

            "gap_map_version": "v0",

            "source_id": (
                self.manifest[
                    "source_id"
                ]
            ),

            "dataset_version": (
                self.manifest[
                    "dataset_version"
                ]
            ),

            "dataset_sha256": (
                self.actual_sha256
            ),

            "canonical_evidence_figure": (
                "2.21"
            ),

            "analysis_space": (
                "log10_thickness_um"
            ),

            "groups": groups,

            "global_internal_gap_ranking": (
                global_ranking
            ),

            "paired_candidate_hint": {
                "microgravity_candidate_um": (
                    micro_candidate
                ),

                "normal_gravity_candidate_um": (
                    normal_candidate
                ),

                "relative_difference": (
                    relative_difference
                ),

                "similar_thickness_candidate": (
                    paired_candidate_possible
                ),

                "interpretation": (
                    "If true, both gravity "
                    "groups independently show "
                    "their largest internal "
                    "coverage gap at similar "
                    "thickness. This is only "
                    "a coverage heuristic, not "
                    "an optimal-experiment claim."
                ),
            },

            "scope_policy": {
                "inside_empirical_domain_only": (
                    True
                ),

                "outside_domain_behavior": (
                    "not_ranked_as_gap; "
                    "prediction system abstains"
                ),

                "uses_model_uncertainty": (
                    False
                ),

                "uses_experimental_uncertainty": (
                    False
                ),

                "uses_digitization_uncertainty": (
                    False
                ),

                "uses_external_figure_2_22_data": (
                    False
                ),

                "uses_theoretical_curves": (
                    False
                ),
            },

            "scientific_limitations": [
                (
                    "Gap score measures only "
                    "spacing between verified "
                    "observations in log-"
                    "thickness space."
                ),

                (
                    "A large spacing gap is not "
                    "the same as high epistemic "
                    "uncertainty."
                ),

                (
                    "This map does not yet "
                    "optimize expected information "
                    "gain."
                ),

                (
                    "This map does not yet use "
                    "BoTorch or Bayesian "
                    "experimental design."
                ),

                (
                    "No extrapolation outside "
                    "the empirical thickness "
                    "domain is recommended."
                ),
            ],

            "status": (
                "empirical_coverage_gap_map_complete"
            ),
        }