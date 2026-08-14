"""Split the ASQ-PHI master file into positive and hard-negative subsets.

Usage:
    python code/split_dataset.py

Reads data/synthetic_clinical_queries.txt (the canonical master) and writes:

    data/positives.txt        queries with >= 1 PHI element
    data/hard_negatives.txt   queries with zero PHI (adversarial structure)

Both output files use the same delimiter format as the master, so the same
parser (parse_dataset.load_asq_phi) works on any of them.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from parse_dataset import load_asq_phi, write_asq_phi


REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_MASTER = REPO_ROOT / "data" / "synthetic_clinical_queries.txt"
DEFAULT_POSITIVES = REPO_ROOT / "data" / "positives.txt"
DEFAULT_HARD_NEGATIVES = REPO_ROOT / "data" / "hard_negatives.txt"


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--master", type=Path, default=DEFAULT_MASTER)
    p.add_argument("--positives", type=Path, default=DEFAULT_POSITIVES)
    p.add_argument("--hard-negatives", type=Path, default=DEFAULT_HARD_NEGATIVES)
    args = p.parse_args()

    records = load_asq_phi(args.master)
    positives = [r for r in records if r["has_phi"]]
    hard_negatives = [r for r in records if not r["has_phi"]]

    write_asq_phi(args.positives, positives)
    write_asq_phi(args.hard_negatives, hard_negatives)

    total_phi = sum(len(r["phi_tags"]) for r in positives)
    print(f"Read     {len(records):>5} records from {args.master}")
    print(f"Wrote    {len(positives):>5} positives  ({total_phi} PHI elements) to {args.positives}")
    print(f"Wrote    {len(hard_negatives):>5} hard negatives to {args.hard_negatives}")


if __name__ == "__main__":
    main()
