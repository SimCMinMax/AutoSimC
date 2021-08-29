"""
Utility functions for AutoSimC.
"""
import datetime
import hashlib
import logging
import os.path
import shutil
from typing import List, TypeVar, Sequence

from settings import settings
try:
    from settings_local import settings
except ImportError:
    pass

from i18n import _


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


def str2bool(v: str) -> bool:
    return v.lower() in ("yes", "true", "t", "1")


def file_checksum(filename):
    h = hashlib.sha256()
    with open(filename, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            h.update(chunk)
    return h.hexdigest()


def cleanup_subdir(subdir):
    if os.path.exists(subdir):
        if not settings.delete_temp_default and not settings.skip_questions:
            if input(
                    _("Do you want to remove subfolder: {}? (Press y to confirm): "
                      ).format(subdir)) != _("y"):
                return
        logging.info(_("Removing subdir '{}'.").format(subdir))
        shutil.rmtree(subdir)


def chop_microseconds(delta: datetime.timedelta):
    """Chop microseconds from a timedelta object"""
    return datetime.timedelta(days=delta.days, seconds=delta.seconds)
