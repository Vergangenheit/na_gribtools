#!/usr/bin/env python3

import sys
from tabulate import tabulate
from na_gribtools.icon.db import *
from na_gribtools.icon.variables import *

action = sys.argv[1].lower()
db = ICONDatabase()

if action == "download":
    for each in sys.argv[2:]:
        filename = db.downloadForecast(int(each))
        print(filename)
elif action == "query":
    allEntries = db.listDatabase()
    lat = float(sys.argv[2])
    lng = float(sys.argv[3])

    outputTable = []
    outputTableHeaders = ["Lat", "Lng", "Forecast"] + ICON_VARIABLE_INDEXES

    for each in allEntries:
        row = []
        with db.getSingleForecast(*each) as x:
            q = x.query(lat, lng)
            row += [q["lat"], q["lng"], q["forecast"]]
            for variableID in ICON_VARIABLE_INDEXES:
                row.append(q[variableID])
        outputTable.append(row)
    
    outputTable.sort(key=lambda i: i[2])
    print(tabulate(outputTable, headers=outputTableHeaders))
elif action == "clean":
    db.cleanUp()
else:
    print("Wrong usage.")
