from __future__ import annotations

import argparse
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from automage_agents.schemas.staff_daily_report_parser import (
    parse_staff_daily_report_file,
    report_to_json,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Parse a staff daily report markdown file into normalized JSON.")
    parser.add_argument("input", help="Path to the markdown report file.")
    parser.add_argument("-o", "--output", help="Optional JSON output path.")
    parser.add_argument(
        "--omit-source-markdown",
        action="store_true",
        help="Do not embed the original markdown in the parsed JSON.",
    )
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    report = parse_staff_daily_report_file(
        args.input,
        include_source_markdown=not args.omit_source_markdown,
    )
    payload = report_to_json(report)

    if args.output:
        Path(args.output).write_text(payload, encoding="utf-8")
        print(args.output)
        return

    print(payload)


if __name__ == "__main__":
    main()
