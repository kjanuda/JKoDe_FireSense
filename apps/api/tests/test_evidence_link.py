from app.schemas.evidence_link import EvidenceLink


def test_unresolved_link_is_not_training_safe():

    link = EvidenceLink(
        link_id="LINK-001",

        source_id="SRC-001",

        left_entity_type="experiment_record",
        left_entity_id="EXP-001",

        right_entity_type="run_condition",
        right_entity_id="RUN-001",

        relation="possible_same_run",

        status="unresolved",

        confidence=0.55,

        supporting_evidence=[
            "Same material and thickness."
        ],

        conflicting_or_missing_evidence=[
            "No explicit same-run identifier."
        ],

        safe_for_training_join=False,
    )

    assert (
        link.safe_for_training_join
        is False
    )

    assert (
        link.status
        == "unresolved"
    )