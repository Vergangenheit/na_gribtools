#!/usr/bin/env python3

import datetime
import re

def timeIdentifierToDatetime(s):
    year = int(s[0:4])
    month = int(s[4:6])
    day = int(s[6:8])
    hour = int(s[8:10])
    return datetime.datetime(year=year, month=month, day=day, hour=hour)

def datetimeToTimeIdentifier(dt):
    return "%04d%02d%02d%02d" % (
        dt.year, dt.month, dt.day, dt.hour
    )
