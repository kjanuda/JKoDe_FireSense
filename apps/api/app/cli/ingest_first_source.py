from app.schemas.source import SourceDocument
from app.services.source_ingestion import (
    ingest_pdf_source,
)


def main():
    source = SourceDocument(
        source_id="SRC-NASA-20210011385",

        external_id="NTRS:20210011385",

        title=(
            "Burning and Suppression of "
            "Solids-II (BASS-II) Summary Report"
        ),

        source_type="technical_memorandum",

        organization=(
            "NASA Glenn Research Center"
        ),

        authors=[
            "Sandra L. Olson",
            "Paul V. Ferkul",
            "Subrata Bhattacharjee",
            "Fletcher J. Miller",
            "Carlos Fernandez-Pello",
            "Shmuel Link",
            "James S. T'ien",
            "Indrek Wichman",
        ],

        publication_year=2021,

        canonical_url=(
            "https://ntrs.nasa.gov/"
            "citations/20210011385"
        ),

        download_url=(
            "https://ntrs.nasa.gov/api/"
            "citations/20210011385/"
            "downloads/TM-20210011385.pdf"
        ),

        notes=(
            "Initial FireSense feasibility source. "
            "Contains BASS-II reduced-gravity "
            "solid-fuel combustion results including "
            "PMMA experiments."
        ),
    )

    result = ingest_pdf_source(source)

    print()
    print("SOURCE INGESTED SUCCESSFULLY")
    print("----------------------------")
    print(
        f"Source ID : {result.source_id}"
    )
    print(
        f"Local path: {result.local_path}"
    )
    print(
        f"SHA-256   : {result.sha256}"
    )
    print(
        f"Size      : "
        f"{result.file_size_bytes} bytes"
    )
    print(
        f"Status    : "
        f"{result.parser_status}"
    )


if __name__ == "__main__":
    main()