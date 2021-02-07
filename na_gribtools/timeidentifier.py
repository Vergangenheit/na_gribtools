#!/usr/bin/env python3

import datetime
import re


def timeIdentifierWithOffsetToDatetime(timeIdentifier: str, delta: float) -> datetime.datetime:
    dt: datetime.datetime = timeIdentifierToDatetime(timeIdentifier)
    return dt + datetime.timedelta(hours=delta)


def timeIdentifierToDatetime(s: str) -> datetime.datetime:
    year: int = int(s[0:4])
    month: int = int(s[4:6])
    day: int = int(s[6:8])
    hour: int = int(s[8:10])
    return datetime.datetime(year=year, month=month, day=day, hour=hour)


def datetimeToTimeIdentifier(dt: datetime.datetime) -> str:
    return "%04d%02d%02d%02d" % (
        dt.year, dt.month, dt.day, dt.hour
    )
