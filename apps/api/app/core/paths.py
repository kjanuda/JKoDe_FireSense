from pathlib import Path


API_ROOT = Path(__file__).resolve().parents[2]

PROJECT_ROOT = API_ROOT.parents[1]

DATA_DIR = PROJECT_ROOT / "data"

RAW_DATA_DIR = DATA_DIR / "raw"

PARSED_DATA_DIR = DATA_DIR / "parsed"

CURATED_DATA_DIR = DATA_DIR / "curated"

FIGURES_DATA_DIR = DATA_DIR / "figures"

GOLD_DATA_DIR = DATA_DIR / "gold"

MANIFESTS_DATA_DIR = DATA_DIR / "manifests"

SOURCES_MANIFEST_PATH = (
    MANIFESTS_DATA_DIR / "sources.json"
)