#!/usr/bin/python
""" Temporary module for tracking down memory leaks """

import logging
import os
import tracemalloc
import linecache

logger = logging.getLogger(__name__)  # pylint: disable=invalid-name


def display_top(source, frame_no, snapshot, key_type='lineno', limit=10):
    """ From https://docs.python.org/3.5/library/tracemalloc.html """
    snapshot = snapshot.filter_traces((
        tracemalloc.Filter(False, "<frozen importlib._bootstrap>"),
        tracemalloc.Filter(False, "<unknown>"),
    ))
    top_stats = snapshot.statistics(key_type)

    logger.info("[%s] Top %s lines - frame: %s", source, limit, frame_no)
    for index, stat in enumerate(top_stats[:limit], 1):
        frame = stat.traceback[0]
        # replace "/path/to/module/file.py" with "module/file.py"
        filename = os.sep.join(frame.filename.split(os.sep)[-2:])
        line = linecache.getline(frame.filename, frame.lineno).strip()
        line = "" if not line else line
        logger.info("#%s: %s:%s: %.1f KiB: '%s'", index, filename, frame.lineno, stat.size / 1024, line)
        
    other = top_stats[limit:]
    if other:
        size = sum(stat.size for stat in other)
        logger.info("%s other: %.1f KiB", len(other), size / 1024)
    total = sum(stat.size for stat in top_stats)
    logger.info("Total allocated size: %.1f KiB", total / 1024)
