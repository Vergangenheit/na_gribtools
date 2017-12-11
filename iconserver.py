#!/usr/bin/env python3

import sys
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

def datetimeToStr(dt):
    return dt.isoformat()

##############################################################################

@route("/<lat:float>/<lng:float>/")
def query(lat, lng):
    global db

    if not checkInput(lat, lng):
        return abort(400, "Latitude and/or longitude invalid.")

    allEntries = db.listDatabase()

    ret = {}

    for each in allEntries:
        with db.getSingleForecast(each) as x:
            q = x.query(lat, lng)
            q["forecast"] = datetimeToStr(q["forecast"])
            q["runtime"] = datetimeToStr(q["runtime"])
            ret[q["forecast"]] = q
    
    return ret


run(host="127.0.0.1", port=7777)
