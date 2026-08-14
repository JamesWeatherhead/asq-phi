"""ASQ-PHI dataset parser.

The canonical file is data/synthetic_clinical_queries.txt, formatted as:

    ===QUERY===
    <query text>
    ===PHI_TAGS===
    {"identifier_type": "NAME", "value": "..."}
    {"identifier_type": "DATE", "value": "..."}

Hard-negative records have an empty ===PHI_TAGS=== section.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Iterable, Union


QUERY_DELIM = "===QUERY==="
PHI_DELIM = "===PHI_TAGS==="


def load_asq_phi(path: Union[str, Path], strict: bool = False) -> list[dict]:
    """Parse an ASQ-PHI file into records.

    Each record is {"query": str, "phi_tags": list[dict], "has_phi": bool}.
    phi_tags entries carry the keys "identifier_type" and "value".

    With strict=True, malformed blocks raise ValueError. The default silently
    skips them to match the notebook validator's behavior.
    """
    text = Path(path).read_text(encoding="utf-8")
    blocks = text.split(QUERY_DELIM)[1:]
    records: list[dict] = []
    for i, block in enumerate(blocks):
        if PHI_DELIM not in block:
            if strict:
                raise ValueError(f"Block {i} missing {PHI_DELIM}")
            continue
        query_part, phi_part = block.split(PHI_DELIM, 1)
        query = query_part.strip()
        if not query:
            if strict:
                raise ValueError(f"Block {i} has empty query")
            continue
        tags: list[dict] = []
        for line in phi_part.splitlines():
            line = line.strip()
            if not line or not line.startswith("{"):
                continue
            try:
                tags.append(json.loads(line))
            except json.JSONDecodeError as e:
                if strict:
                    raise ValueError(f"Block {i} bad JSON: {line!r}") from e
                continue
        records.append({
            "query": query,
            "phi_tags": tags,
            "has_phi": bool(tags),
        })
    return records


def format_block(record: dict) -> str:
    """Format a record back into the canonical delimiter block."""
    lines = [QUERY_DELIM, record["query"], PHI_DELIM]
    for tag in record["phi_tags"]:
        lines.append(json.dumps(tag))
    return "\n".join(lines)


def write_asq_phi(path: Union[str, Path], records: Iterable[dict]) -> None:
    """Write records to file in the canonical delimiter format.

    Records are separated by one blank line, and the file ends with a newline.
    """
    with open(path, "w", encoding="utf-8") as f:
        for i, record in enumerate(records):
            if i > 0:
                f.write("\n\n")
            f.write(format_block(record))
        f.write("\n")
