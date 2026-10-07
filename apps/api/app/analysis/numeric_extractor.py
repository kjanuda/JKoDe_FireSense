
import re
from typing import Any

from app.schemas.measurement_proposal import (
    MeasurementProposal,
    NumericMention,
)


# ============================================================
# Numeric extraction patterns
# ============================================================

OXYGEN_PATTERNS = (
    re.compile(
        r"(?P<value>\d+(?:\.\d+)?)\s*"
        r"(?:percent|%)\s*"
        r"(?:O2|O₂|oxygen)\b",
        re.IGNORECASE,
    ),
    re.compile(
        r"\b(?:O2|O₂|oxygen)"
        r"(?:\s+(?:level|concentration))?"
        r"\s*"
        r"(?:"
        r"=|:|of|at|was|is|to|"
        r"can\s+be\s+adjusted\s+to"
        r")?"
        r"\s*"
        r"(?P<value>\d+(?:\.\d+)?)\s*"
        r"(?:percent|%)\b",
        re.IGNORECASE,
    ),
)


PRESSURE_KPA_PATTERN = re.compile(
    r"(?P<value>\d+(?:\.\d+)?)\s*"
    r"k\s*Pa",
    re.IGNORECASE,
)


PRESSURE_ATM_PATTERN = re.compile(
    r"(?P<value>\d+(?:\.\d+)?)\s*atm\b",
    re.IGNORECASE,
)


FLOW_PATTERN = re.compile(
    r"(?P<value>\d+(?:\.\d+)?)\s*"
    r"cm\s*/\s*s",
    re.IGNORECASE,
)


SPREAD_MM_S_PATTERN = re.compile(
    r"(?P<value>\d+(?:\.\d+)?)\s*"
    r"mm\s*/\s*s",
    re.IGNORECASE,
)


SPREAD_MM_MIN_PATTERN = re.compile(
    r"(?P<value>\d+(?:\.\d+)?)\s*"
    r"mm\s*/\s*min",
    re.IGNORECASE,
)


THICKNESS_UM_PATTERN = re.compile(
    r"(?P<value>\d+(?:\.\d+)?)\s*"
    r"(?:µ|μ|u)\s*m"
    r"(?:[-\s]*thick)?",
    re.IGNORECASE,
)


FIGURE_PATTERN = re.compile(
    r"Figure\s+([A-Za-z]?\d+(?:\.\d+)?)",
    re.IGNORECASE,
)


TABLE_PATTERN = re.compile(
    r"Table\s+([A-Za-z]?\d+(?:\.\d+)?)",
    re.IGNORECASE,
)


# ============================================================
# Numeric mention helper
# ============================================================

def mention_from_match(
    match: re.Match,
    unit: str,
    normalized_value: float,
    normalized_unit: str,
) -> NumericMention:
    """
    Convert a regex match into a NumericMention while
    preserving the original matched text and character span.
    """

    return NumericMention(
        value=float(
            match.group("value")
        ),
        unit=unit,
        normalized_value=normalized_value,
        normalized_unit=normalized_unit,
        matched_text=match.group(0),
        start_char=match.start(),
        end_char=match.end(),
    )


# ============================================================
# Duplicate handling
# ============================================================

def unique_mentions(
    mentions: list[NumericMention],
) -> list[NumericMention]:
    """
    Remove duplicate numeric mentions.

    Two mentions are considered duplicates when their numeric
    value and normalized representation are identical.
    """

    seen = set()
    result = []

    for mention in mentions:
        key = (
            mention.value,
            mention.unit,
            mention.normalized_value,
            mention.normalized_unit,
        )

        if key in seen:
            continue

        seen.add(key)
        result.append(mention)

    return result


# ============================================================
# Oxygen extraction
# ============================================================

def extract_oxygen(
    text: str,
) -> list[NumericMention]:
    """
    Extract oxygen concentration values.

    Supported examples:

        20.7 percent O2
        20.7% O2
        O2 level = 21 percent
        O2 concentration was 21%
        oxygen was 21 percent
        O2 level can be adjusted to 21 percent

    Normalized representation:

        percentage -> fraction

        20.7% -> 0.207
    """

    mentions = []

    for pattern in OXYGEN_PATTERNS:
        for match in pattern.finditer(text):
            percent = float(
                match.group("value")
            )

            mentions.append(
                mention_from_match(
                    match=match,
                    unit="%",
                    normalized_value=(
                        percent / 100.0
                    ),
                    normalized_unit="fraction",
                )
            )

    return unique_mentions(mentions)


# ============================================================
# Pressure extraction
# ============================================================

def extract_pressure(
    text: str,
) -> list[NumericMention]:
    """
    Extract pressure values in kPa and atm.

    Normalized representation:

        kPa -> kPa

        atm -> kPa
    """

    mentions = []

    # kPa
    for match in PRESSURE_KPA_PATTERN.finditer(text):
        value = float(
            match.group("value")
        )

        mentions.append(
            mention_from_match(
                match=match,
                unit="kPa",
                normalized_value=value,
                normalized_unit="kPa",
            )
        )

    # atm
    for match in PRESSURE_ATM_PATTERN.finditer(text):
        atm = float(
            match.group("value")
        )

        mentions.append(
            mention_from_match(
                match=match,
                unit="atm",
                normalized_value=(
                    atm * 101.325
                ),
                normalized_unit="kPa",
            )
        )

    return unique_mentions(mentions)


# ============================================================
# Flow extraction
# ============================================================

def extract_flow(
    text: str,
) -> list[NumericMention]:
    """
    Extract opposed-flow velocity values.

    Example:

        2.5 cm/s
    """

    mentions = []

    for match in FLOW_PATTERN.finditer(text):
        value = float(
            match.group("value")
        )

        mentions.append(
            mention_from_match(
                match=match,
                unit="cm/s",
                normalized_value=value,
                normalized_unit="cm/s",
            )
        )

    return unique_mentions(mentions)


# ============================================================
# Flame spread-rate extraction
# ============================================================

def extract_spread_rate(
    text: str,
) -> list[NumericMention]:
    """
    Extract flame spread-rate values.

    Supported units:

        mm/s
        mm/min

    Normalized representation:

        mm/s -> mm/s

        mm/min -> mm/s
    """

    mentions = []

    # mm/s
    for match in SPREAD_MM_S_PATTERN.finditer(text):
        value = float(
            match.group("value")
        )

        mentions.append(
            mention_from_match(
                match=match,
                unit="mm/s",
                normalized_value=value,
                normalized_unit="mm/s",
            )
        )

    # mm/min -> mm/s
    for match in SPREAD_MM_MIN_PATTERN.finditer(text):
        value = float(
            match.group("value")
        )

        mentions.append(
            mention_from_match(
                match=match,
                unit="mm/min",
                normalized_value=(
                    value / 60.0
                ),
                normalized_unit="mm/s",
            )
        )

    return unique_mentions(mentions)


# ============================================================
# Thickness extraction
# ============================================================

def extract_thickness(
    text: str,
) -> list[NumericMention]:
    """
    Extract material thickness values.

    Supported examples:

        100 µm
        100µm
        100 µ m
        100µ m
        100 μm
        100 μ m
        100 um
        100u m
        100 µm-thick
        100 µm thick
    """

    mentions = []

    for match in THICKNESS_UM_PATTERN.finditer(text):
        value = float(
            match.group("value")
        )

        mentions.append(
            mention_from_match(
                match=match,
                unit="µm",
                normalized_value=value,
                normalized_unit="µm",
            )
        )

    return unique_mentions(mentions)


# ============================================================
# Gravity detection
# ============================================================

def detect_gravity_regime(
    text: str,
) -> str:
    """
    Detect whether a block contains:

        microgravity
        normal gravity
        both
        unknown
    """

    lowered = text.lower()

    microgravity = (
        "microgravity" in lowered
        or "0g" in lowered
        or "international space station" in lowered
        or " iss " in f" {lowered} "
    )

    normal_gravity = (
        "normal-gravity" in lowered
        or "normal gravity" in lowered
        or "1g" in lowered
        or "downward flame spread" in lowered
    )

    if microgravity and normal_gravity:
        return "mixed"

    if microgravity:
        return "microgravity"

    if normal_gravity:
        return "normal_gravity"

    return "unknown"


# ============================================================
# Evidence-form detection
# ============================================================

def detect_evidence_form(
    tags: list[str],
) -> str:
    """
    Determine whether the evidence is:

        prose
        figure-linked
        table-linked
        mixed
    """

    has_figure = "figure" in tags
    has_table = "table" in tags

    if has_figure and has_table:
        return "mixed"

    if has_figure:
        return "figure_linked"

    if has_table:
        return "table_linked"

    return "prose"


# ============================================================
# Measurement proposal builder
# ============================================================

def build_measurement_proposal(
    block: dict[str, Any],
    proposal_id: str,
    source_id: str,
) -> MeasurementProposal:
    """
    Build a MeasurementProposal from an extracted document block.

    Important review logic:

    1. Numeric measurements are extracted once and reused.
    2. A figure/table reference does not automatically force
       digitization when a direct numerical outcome is already
       present in the prose.
    3. Mixed-gravity blocks remain pending and receive a warning
       requiring manual separation before training-row creation.
    """

    text = block["text"]
    tags = block.get("tags", [])

    # ---------------------------------------------------------
    # Figure references
    # ---------------------------------------------------------

    figure_refs = [
        match.group(1)
        for match in FIGURE_PATTERN.finditer(text)
    ]

    # ---------------------------------------------------------
    # Table references
    # ---------------------------------------------------------

    table_refs = [
        match.group(1)
        for match in TABLE_PATTERN.finditer(text)
    ]

    # ---------------------------------------------------------
    # Warnings
    # ---------------------------------------------------------

    warnings: list[str] = []

    # ---------------------------------------------------------
    # Gravity regime
    # ---------------------------------------------------------

    gravity_regime = detect_gravity_regime(text)

    if gravity_regime == "mixed":
        warnings.append(
            "Block contains both microgravity "
            "and normal-gravity context."
        )

        warnings.append(
            "Do not create a training row "
            "until normal-gravity and "
            "microgravity observations "
            "are manually separated."
        )

    # ---------------------------------------------------------
    # Content-type warnings
    # ---------------------------------------------------------

    if "computational" in tags:
        warnings.append(
            "Block contains computational/model content."
        )

    if "theory" in tags:
        warnings.append(
            "Block contains theoretical content."
        )

    # ---------------------------------------------------------
    # Extract numeric measurements ONCE
    # ---------------------------------------------------------

    thickness_mentions = extract_thickness(text)

    oxygen_mentions = extract_oxygen(text)

    pressure_mentions = extract_pressure(text)

    flow_mentions = extract_flow(text)

    spread_mentions = extract_spread_rate(text)

    # ---------------------------------------------------------
    # Direct outcome detection
    # ---------------------------------------------------------

    # A direct flame-spread result in prose means the block
    # already contains an extractable numerical outcome.
    #
    # Example:
    #
    #     "Average spread rate was 2.0 mm/s."
    #
    # Even if the same paragraph says "Figure 4", we do not
    # automatically require figure digitization.

    has_direct_outcome = bool(
        spread_mentions
    )

    # ---------------------------------------------------------
    # Figure/table review requirements
    # ---------------------------------------------------------

    needs_figure = (
        bool(figure_refs)
        and not has_direct_outcome
    )

    needs_table = (
        bool(table_refs)
        and not has_direct_outcome
    )

    # ---------------------------------------------------------
    # Review status
    # ---------------------------------------------------------

    review_status = "pending"

    # Mixed gravity is always kept pending.
    #
    # We intentionally do not automatically move it into
    # accepted/training-ready status because the observations
    # may represent different experimental regimes.

    if gravity_regime == "mixed":
        review_status = "pending"

    elif needs_figure:
        review_status = "needs_figure_digitization"

    elif needs_table:
        review_status = "needs_table_extraction"

    # ---------------------------------------------------------
    # Build proposal
    # ---------------------------------------------------------

    return MeasurementProposal(
        proposal_id=proposal_id,
        source_id=source_id,
        study_id=block["study_id"],
        block_id=block["block_id"],
        pages=block["pages"],

        evidence_form=detect_evidence_form(tags),

        gravity_regime=gravity_regime,

        # Reuse the already extracted values.
        thickness_mentions=thickness_mentions,
        oxygen_mentions=oxygen_mentions,
        pressure_mentions=pressure_mentions,
        flow_mentions=flow_mentions,
        spread_rate_mentions=spread_mentions,

        figure_refs=figure_refs,
        table_refs=table_refs,

        needs_figure_digitization=needs_figure,
        needs_table_extraction=needs_table,

        review_status=review_status,

        warnings=warnings,

        raw_text=text,
    )

