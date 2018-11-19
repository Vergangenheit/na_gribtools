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
    return dt.isoformat() + "Z"

def retrieveForecasts(lat, lng):
    global db
    allEntries = db.listDatabase()
    ret = {}
    for each in allEntries:
        with db.getSingleForecast(each) as x:
            q = x.query(lat, lng)
            q["forecast"] = datetimeToStr(q["forecast"])
            q["runtime"] = datetimeToStr(q["runtime"])
            ret[q["forecast"]] = q
    return ret

##############################################################################

@route("/<lat:float>/<lng:float>/")
def query(lat, lng):
    if not checkInput(lat, lng):
        return abort(400, "Latitude and/or longitude invalid.")
    forecasts = retrieveForecasts(lat, lng)
    countForecasts = len(forecasts)
    metadata = {
        "count": countForecasts,
        "queryCoordinates": [lat, lng],
    }
    if countForecasts > 0:
        sampleForecast = forecasts[list(forecasts.keys())[0]]
        forecastLat = sampleForecast["lat"]
        forecastLng = sampleForecast["lng"]
        metadata["forecastCoordinates"] = [forecastLat, forecastLng]
    else:
        metadata["forecastCoordinates"] = [lat, lng]

    return { "metadata": metadata, "forecasts": forecasts }

@get("/<region:re:[a-z]+>/<varname>/")
def listImages(region, varname):
    if not (region in ICON_IMAGE_REGIONS and varname in ICON_IMAGE_OUTPUT):
        return abort(404, "Requested combination is invalid.")

    ending = ".%s.png" % region
    lst = [
        i[:-len(ending)][-10:] \
        for i in os.listdir(config.workDir)\
        if (\
            i.startswith("image") and \
            i.endswith(ending) and \
            varname in i
        )
    ]
    return "<br />".join([
        """<a href="/%s/%s/%s">%s</a>""" % (
            region, varname, each, each
        ) for each in lst
    ])

@get("/<region:re:[a-z]+>/<varname>/<timestamp:re:[0-9]{10}>")
def serveImage(region, varname, timestamp):
    if not (region in ICON_IMAGE_REGIONS and varname in ICON_IMAGE_OUTPUT):
        return abort(404, "Requested combination is invalid.")
    filename = "image-%s-%s.%s.png" % (varname, timestamp, region)
    fullpath = config.workDir(filename)
    if not os.path.isfile(fullpath):
        return abort(404, "File does not exist.")
    return static_file(filename, root=config.workDir)


run(host="127.0.0.1", port=7777)
