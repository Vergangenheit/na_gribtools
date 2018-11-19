#!/usr/bin/env python3

import sys
from tabulate import tabulate

from na_gribtools.config import ConfigParser
from na_gribtools.icon.db import *
from na_gribtools.icon.grb2toimages import *
from na_gribtools.icon.variables import *

config = ConfigParser("./config.yaml")

action = sys.argv[1].lower()
db = ICONDatabase(config)

if action == "download":
    base = sys.argv[2]
    if base == "now":
        func = db.downloadForecastFromNow
    elif base == "zero":
        func = db.downloadForecastFromRuntime
    else:
        print("Usage: python3 iconmanage.py download <now|zero> hour(s)")
        exit(1)
    for each in sys.argv[3:]:
        filename = func(int(each))
        print(filename)

elif action == "query":
    allEntries = db.listDatabase()
    lat = float(sys.argv[2])
    lng = float(sys.argv[3])

    outputTable = []
    outputTableHeaders = [
        "Lat",
        "Lng",
        "Forecast(UTC)"
    ] + ICON_VARIABLE_INDEXES

    for each in allEntries:
        row = []
        with db.getSingleForecast(each) as x:
            q = x.query(lat, lng)
            row += [q["lat"], q["lng"], q["forecast"]]
            for variableID in ICON_VARIABLE_INDEXES:
                row.append(q[variableID])
        outputTable.append(row)
    
    outputTable.sort(key=lambda i: i[2])
    print(tabulate(outputTable, headers=outputTableHeaders))

elif action == "image":
    for task in db.listGRB2ForImages():
        doGRB2ToImageTask(task, config=config)

elif action == "clean":
    db.cleanUp()

else:
    print("Wrong usage.")
