"""
Utility functions for AutoSimC.
"""
import datetime
import hashlib
from typing import List, TypeVar, Sequence


_T = TypeVar('_T')


def stable_unique(seq: Sequence[_T]) -> List[_T]:
    """
    Filter sequence to only contain unique elements, in a stable order
    This is a replacement for x = list(set(x)), which does not lead to
    deterministic or 'stable' output.
    Credit to https://stackoverflow.com/a/480227
    """
    seen = set()
    seen_add = seen.add
    return [x for x in seq if not (x in seen or seen_add(x))]


def file_checksum(filename):
    h = hashlib.sha256()
    with open(filename, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            h.update(chunk)
    return h.hexdigest()


def chop_microseconds(delta: datetime.timedelta):
    """Chop microseconds from a timedelta object"""
    return datetime.timedelta(days=delta.days, seconds=delta.seconds)
