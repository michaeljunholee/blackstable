"""Stable, collision-free ID generation for CircleUSDC project.

IDs follow the format `CU-<PREFIX>-<NNNN>` where PREFIX is a 3-letter code
(ACT, TRG, INC, REQ, POL, IMP, ENT, SRC) and NNNN is a zero-padded
monotonically increasing integer.
"""
from __future__ import annotations

import re
from typing import Iterable

_VALID_PREFIXES = {"ACT", "TRG", "INC", "REQ", "POL", "IMP", "ENT", "SRC"}
_ID_PATTERN = re.compile(r"^CU-([A-Z]{3})-(\d{4,})$")


def parse_id(id_str: str) -> tuple[str, int]:
    """Parse an ID into (prefix, number). Raises ValueError on malformed input."""
    match = _ID_PATTERN.match(id_str)
    if not match:
        raise ValueError(f"malformed id: {id_str!r}")
    return match.group(1), int(match.group(2))


def next_available(prefix: str, existing: Iterable[str]) -> int:
    """Return the next integer available for `prefix`, given `existing` IDs."""
    if prefix not in _VALID_PREFIXES:
        raise ValueError(f"invalid prefix: {prefix!r}")
    highest = 0
    for id_str in existing:
        try:
            p, n = parse_id(id_str)
        except ValueError:
            continue
        if p == prefix and n > highest:
            highest = n
    return highest + 1


def mint_id(prefix: str, existing: Iterable[str]) -> str:
    """Mint a new ID for the given prefix, monotonically above all existing IDs."""
    n = next_available(prefix, existing)
    # Pad to 4 digits minimum; expand as needed.
    return f"CU-{prefix}-{n:04d}"
