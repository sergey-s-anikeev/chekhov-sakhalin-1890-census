from __future__ import annotations

import argparse
from pathlib import Path

from sakhalin_conversion_helpers_v11 import extract_pdf_text_pages


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Extract page-by-page text from a readable/searchable PDF."
    )

    parser.add_argument(
        "--pdf",
        required=True,
        help="Path to the source PDF file."
    )

    parser.add_argument(
        "--out",
        default="data/raw/extracted_pages",
        help="Output folder for extracted page text files."
    )

    args = parser.parse_args()

    pdf_path = Path(args.pdf)
    output_dir = Path(args.out)

    if not pdf_path.exists():
        raise FileNotFoundError(f"PDF file not found: {pdf_path}")

    extract_pdf_text_pages(pdf_path, output_dir)

    print(f"Extracted page text files to: {output_dir}")


if __name__ == "__main__":
    main()
