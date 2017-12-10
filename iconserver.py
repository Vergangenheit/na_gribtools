#!/usr/bin/env python3

import sys
from tabulate import tabulate
from bottle import *

from na_gribtools.config import ConfigParser
from na_gribtools.icon.db import *
from na_gribtools.icon.variables import *

config = ConfigParser("./config.yaml")
db = ICONDatabase(config)

##############################################################################

def checkInput(lat, lng):
    try:    
        assert type(lat) == float
        assert type(lng) == float
        if lat > 90 or lat < -90: return False
        if lng <= -180 or lng > 180: return False
    except:
        return False
    return True

##############################################################################

@route("/<lat:float>/<lng:float>/")
def query(lat, lng):
    global db

    if not checkInput(lat, lng):
        return abort(400, "Latitude and/or longitude invalid.")

    allEntries = db.listDatabase()

    outputTable = []
    outputTableHeaders = [
        "Lat",
        "Lng",
        "Forecast(UTC)"
    ] + ICON_VARIABLE_INDEXES

    for each in allEntries:
        row = []
        with db.getSingleForecast(*each) as x:
            q = x.query(lat, lng)
            row += [q["lat"], q["lng"], q["forecast"]]
            for variableID in ICON_VARIABLE_INDEXES:
                row.append(q[variableID])
        outputTable.append(row)
    
    outputTable.sort(key=lambda i: i[2])
    return (tabulate(outputTable, headers=outputTableHeaders))


run(host="127.0.0.1", port=7777)
