#!/usr/bin/env python3
"""NRFS score — weighted feature-parity scorer.

Reads the NRFS feature matrix (nrfs/features.csv) and prints the parity score,
the must-have completion state, the weakest areas first, and the missing list
in build order. Standard library only, no network, no installs.

Matrix columns:
    id, area, feature, priority (must|should|could), original (yes|no|partial),
    clone (yes|partial|no|skip), note

Scoring rules (fixed, printed with the result):
    weight: must=3, should=2, could=1
    partial counts as half; skipped rows score nothing and are excluded;
    bonus rows (original=no, clone=yes) are excluded from the score and listed
    as additions; any must row not fully done means NOT SHIPPABLE.

Usage:
    python3 nrfs_score.py nrfs/features.csv
    python3 nrfs_score.py nrfs/features.csv --markdown >> nrfs/audit.md
"""

from __future__ import annotations

import argparse
import csv
import sys
from collections import defaultdict
from pathlib import Path

WEIGHTS = {"must": 3, "should": 2, "could": 1}
DONE = {"yes": 1.0, "partial": 0.5, "no": 0.0}


def _norm(value: str) -> str:
    return (value or "").strip().lower()


def load_rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))
    if not rows:
        raise SystemExit(f"error: {path} has no rows")
    missing = {"id", "priority", "clone"} - {k.lower() for k in rows[0]}
    if missing:
        raise SystemExit(
            f"error: {path} is missing required column(s): {', '.join(sorted(missing))}"
        )
    return rows


def score(rows: list[dict[str, str]]) -> dict:
    applicable = achieved = 0.0
    per_area: dict[str, list[float]] = defaultdict(list)
    musts_total = musts_done = 0
    missing_must: list[str] = []
    bonus: list[str] = []
    unknown_priority = 0

    for row in rows:
        rid = _norm(row.get("id")) or "?"
        area = _norm(row.get("area")) or "general"
        priority = _norm(row.get("priority"))
        original = _norm(row.get("original"))
        clone = _norm(row.get("clone"))
        feature = (row.get("feature") or "").strip()

        if clone == "skip":
            continue
        if original == "no" and clone in DONE:
            bonus.append(f"{rid} {feature}")
            continue
        if priority not in WEIGHTS:
            unknown_priority += 1
            continue
        weight = WEIGHTS[priority]
        ratio = DONE.get(clone, 0.0)

        applicable += weight
        achieved += weight * ratio
        per_area[area].append(ratio)
        if priority == "must":
            musts_total += 1
            if clone == "yes":
                musts_done += 1
            else:
                state = "partial" if clone == "partial" else "not started"
                missing_must.append(f"{rid} [{state}] {feature}")

    pct = round(100 * achieved / applicable) if applicable else 0
    areas = sorted(
        (
            (area, round(100 * sum(r) / len(r)), len(r))
            for area, r in per_area.items()
        ),
        key=lambda item: (item[1], -item[2]),
    )
    return {
        "pct": pct,
        "achieved": achieved,
        "applicable": applicable,
        "musts_total": musts_total,
        "musts_done": musts_done,
        "missing_must": missing_must,
        "bonus": bonus,
        "areas": areas,
        "unknown_priority": unknown_priority,
    }


def report(result: dict, source: Path, markdown: bool = False) -> str:
    lines: list[str] = []
    if markdown:
        lines.append("## NRFS parity score")
        lines.append("")
        lines.append(f"- **score: {result['pct']}%** ({result['achieved']:g} of "
                     f"{result['applicable']:g} weighted points) — `{source}`")
        lines.append(f"- must-haves: {result['musts_done']}/{result['musts_total']} done")
    else:
        bar = "#" * (result["pct"] // 5) + "." * (20 - result["pct"] // 5)
        lines.append(f"NRFS parity score — {source}")
        lines.append(f"  [{bar}] {result['pct']}%")
        lines.append(f"  weighted: {result['achieved']:g} of {result['applicable']:g} "
                     "(must=3 should=2 could=1, partial=half)")
        lines.append(f"  must-haves: {result['musts_done']}/{result['musts_total']} done")

    if result["areas"]:
        lines.append("  weakest areas first:")
        for area, pct, count in result["areas"][:5]:
            lines.append(f"    - {area}: {pct}% ({count} features)")
    if result["missing_must"]:
        lines.append("  MISSING must-haves (build order):")
        lines.extend(f"    - {m}" for m in result["missing_must"])
    if result["bonus"]:
        shown = ", ".join(result["bonus"][:5])
        more = f" (+{len(result['bonus']) - 5} more)" if len(result["bonus"]) > 5 else ""
        lines.append(f"  additions beyond the matrix: {shown}{more}")
    if result["unknown_priority"]:
        lines.append(f"  note: {result['unknown_priority']} row(s) had an unknown "
                     "priority (use must/should/could) — excluded")

    verdict = (
        "NOT SHIPPABLE — incomplete must-haves."
        if result["missing_must"]
        else "all must-haves done."
    )
    lines.append(f"  verdict: {verdict}")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="NRFS feature-parity scorer")
    parser.add_argument("matrix", type=Path, help="path to nrfs/features.csv")
    parser.add_argument("--markdown", action="store_true",
                        help="print a markdown summary (for nrfs/audit.md)")
    args = parser.parse_args()

    if not args.matrix.is_file():
        print(f"error: {args.matrix} not found", file=sys.stderr)
        return 2

    result = score(load_rows(args.matrix))
    print(report(result, args.matrix, markdown=args.markdown))
    return 1 if result["missing_must"] else 0


if __name__ == "__main__":
    sys.exit(main())
