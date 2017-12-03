#!/usr/bin/env python3

import os
import sys
import subprocess
import datetime
import math

from .variables import *


DATASET_DELAY = datetime.timedelta(hours=3)



class ICONDatabase:

    def __init__(self, localDir="/tmp/na_dwd/"):
        pass

    def __getURL(self, variableID, timestamp, forecastHour=6):
        vName, vLevel, vBand = ICON_VARIABLES[variableID]
        URL = "https://opendata.dwd.de/weather/icon/global/grib/"
        URL += timestamp[-2:] + "/" + vName.lower() + "/"
        URL += "ICON_iko_%s_elements_world_%s_%s_%03d.grib2.bz2" % (\
            vLevel,
            vName.upper(),
            timestamp,
            forecastHour
        )
        return URL

    def downloadNew(self, variableID):
        assert variableID in ICON_VARIABLES
        nowTime = datetime.datetime.utcnow() 
        lastTime = nowTime - DATASET_DELAY
        
        downloadHour = math.floor(lastTime.hour/6.0) * 6
        downloadTimestamp = "%4d%02d%02d%02d" % (\
            lastTime.year,
            lastTime.month,
            lastTime.day,
            downloadHour
        )

        return self.__getURL(variableID, downloadTimestamp)
