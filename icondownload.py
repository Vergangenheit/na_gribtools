#!/usr/bin/env python3

from na_gribtools.icon.db import *

db = ICONDatabase()
print(db.downloadForecast(6))
