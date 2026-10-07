import json

from app.core.paths import FIGURES_DATA_DIR


SOURCE_ID = "SRC-NASA-20210011385"


def load_json(path):
    if not path.exists():
        raise FileNotFoundError(
            f"Missing file: {path}"
        )

    return json.loads(
        path.read_text(
            encoding="utf-8"
        )
    )


def save_json(path, payload):
    path.write_text(
        json.dumps(
            payload,
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )


def main():

    figure_dir = (
        FIGURES_DATA_DIR
        / SOURCE_ID
        / "digitization"
        / "figure_2_22"
    )

    review_path = (
        figure_dir
        / "figure_2_22_final_review.json"
    )

    validation_path = (
        figure_dir
        / "figure_2_22_final_validation.json"
    )

    review = load_json(
        review_path
    )

    validation = load_json(
        validation_path
    )

    # Safety checks.
    if (
        validation.get(
            "automatic_validation"
        )
        != "pass"
    ):
        raise ValueError(
            "Automatic validation has "
            "not passed."
        )

    if (
        validation.get(
            "total_point_count"
        )
        != 33
    ):
        raise ValueError(
            "Expected exactly 33 "
            "experimental points."
        )

    if review.get(
        "theoretical_curves_included"
    ):
        raise ValueError(
            "Theoretical curves must "
            "remain excluded."
        )

    # Human visual review completed.
    review[
        "verification_status"
    ] = "human_overlay_verified"

    review[
        "human_verified"
    ] = True

    review[
        "overlay_verified"
    ] = True

    review.setdefault(
        "review_notes",
        [],
    )

    review[
        "review_notes"
    ].append(
        "Final 33-point overlay visually "
        "reviewed and passed. Marker centres "
        "align with experimental markers; "
        "legend markers and theoretical "
        "curves are excluded."
    )

    validation[
        "visual_overlay_status"
    ] = "pass"

    validation[
        "final_status"
    ] = "pass"

    validation[
        "human_review_notes"
    ] = [
        (
            "All 33 review boxes align "
            "with experimental marker centres."
        ),
        (
            "No legend example markers "
            "were selected."
        ),
        (
            "Thermally thin and thermally "
            "thick theoretical curves "
            "were not digitized as "
            "experimental evidence."
        ),
        (
            "Cross-study provenance remains "
            "unresolved and must be audited "
            "before modeling."
        ),
    ]

    save_json(
        review_path,
        review,
    )

    save_json(
        validation_path,
        validation,
    )

    print()
    print(
        "FIGURE 2.22 REVIEW LOCK"
    )

    print(
        "-----------------------"
    )

    print()
    print(
        "Experimental points : 33"
    )

    print(
        "Automatic review    : PASS"
    )

    print(
        "Visual overlay      : PASS"
    )

    print(
        "Theory curves       : EXCLUDED"
    )

    print()
    print(
        "Review status:"
    )

    print(
        "  human_overlay_verified"
    )

    print()
    print(
        "IMPORTANT:"
    )

    print(
        "  Figure 2.22 points are "
        "NOT yet training-ready."
    )

    print(
        "  Cross-study provenance "
        "must be resolved next."
    )


if __name__ == "__main__":
    main()