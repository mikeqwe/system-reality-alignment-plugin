#!/usr/bin/env python3
"""Scaffold a System Reality Alignment Markdown artifact."""

from __future__ import annotations

import argparse
from datetime import date
from pathlib import Path
import re
import sys

MODES = {
    "design": "design.md",
    "review": "review.md",
    "plan": "plan.md",
    "repair": "repair.md",
    "implementation": "implementation.md",
    "operations": "operations.md",
    "evaluation": "evaluation.md",
    "decision-record": "decision-record.md",
    "data-contract": "data-contract.md",
}


def slugify(value: str) -> str:
    value = value.strip().lower()
    value = re.sub(r"[^a-z0-9]+", "-", value)
    return value.strip("-") or "system"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mode", choices=sorted(MODES))
    parser.add_argument("--system", required=True, help="System, domain, or intervention name")
    parser.add_argument("--output", type=Path, help="Output Markdown path")
    parser.add_argument("--date", default=date.today().isoformat(), help="Document date (YYYY-MM-DD)")
    parser.add_argument("--force", action="store_true", help="Overwrite an existing output file")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    template_dir = Path(__file__).resolve().parent.parent / "assets" / "templates"
    template_path = template_dir / MODES[args.mode]
    if not template_path.is_file():
        print(f"error: template not found: {template_path}", file=sys.stderr)
        return 2

    output = args.output or Path("docs/system-reality") / f"{slugify(args.system)}-{args.mode}.md"
    if output.exists() and not args.force:
        print(f"error: output already exists: {output}; use --force to overwrite", file=sys.stderr)
        return 2

    text = template_path.read_text(encoding="utf-8")
    text = text.replace("{{SYSTEM_NAME}}", args.system.strip())
    text = text.replace("{{DATE}}", args.date)

    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(text, encoding="utf-8")
    print(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
