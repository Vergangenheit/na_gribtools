#!/usr/bin/env python3
"""
Convert .grb2 file into an image based on predefined instructions.

`task` is a dict in format:
    {
        "path": fullpath,
        "item": interested,
        "config": ICON_IMAGE_OUTPUT[interested],
        "runtime": runTime,
        "forecast": forecastTime,
    }
    see `na_gribtools/icon/db.py` for more information.

"""


def doGRB2ToImageTask(task):
    print(task)
