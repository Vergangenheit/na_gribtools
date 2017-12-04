#!/usr/bin/env python3

import os
import sys
import subprocess
import datetime
import math

from .variables import *
from .dbcache import *

DATASET_DELAY = datetime.timedelta(hours=3)



class ICONDatabase:

    def __init__(self, tempDir="/tmp/na_dwd/", resourceDir="./resources/"):
        self.resourceDir = resourceDir
        self.tempDir = tempDir

    def __getURL(self, variableID, timeIdentifier, hours=6):
        """Generate a download URL for a given variable defined in
        `variables.py`, with a given time identifier, and a hour which the
        dataset is calculated for in the future.

        For example: 
            timeIdentifier=2017120300 -> model run 2017-12-03 00:00 UTC
            hours=24                  -> model prediction for 0+24h
        we get data for 2017-12-04 00:00 UTC.

        `hours` must be an integer. 0 <= hours <= 180 can be accepted, where
        when hours <= 78, any integer is available. For hours > 78, it's only
        valid if hours % 3 == 0, e.g. 81, 84, 87...
        """
        assert variableID in ICON_VARIABLES
        try:
            assert type(hours) == int and hours >= 0 and hours <= 180
            if hours > 78: assert hours % 3 == 0
        except:
            raise Exception("Invalid forecast hour.")

        vName, vLevel, vBand = ICON_VARIABLES[variableID]
        URL = "https://opendata.dwd.de/weather/icon/global/grib/"
        URL += timeIdentifier[-2:] + "/" + vName.lower() + "/"
        URL += "ICON_iko_%s_elements_world_%s_%s_%03d.grib2.bz2" % (\
            vLevel,
            vName.upper(),
            timeIdentifier,
            hours
        )
        return URL

    def __getDownloadTimeInfo(self):
        lastTime = datetime.datetime.utcnow() - DATASET_DELAY
        downloadHour = math.floor(lastTime.hour/6.0) * 6
        downloadTime = datetime.datetime(
            lastTime.year, lastTime.month, lastTime.day, downloadHour
        )
        return "%4d%02d%02d%02d" % (\
            downloadTime.year,
            downloadTime.month,
            downloadTime.day,
            downloadHour
        ), downloadTime

    def downloadForecast(self, forecastHoursFromNow=6):
        """Download a set of forecasts and compile them into a database
        that we will read more easily. `forecastHoursFromNow` will be
        used to calculate the downloads needed from the latest whole hour,
        e.g. if it's 07:11 now, forecast in 1 hour will be 08:00."""

        # Decide which time is to be downloaded from server

        timeIdentifier, downloadTime = self.__getDownloadTimeInfo()
        nowTime = datetime.datetime.utcnow()
        roundedNowTime = datetime.datetime(
            nowTime.year, nowTime.month, nowTime.day, nowTime.hour)
        forecastTime = roundedNowTime +\
            datetime.timedelta(hours=forecastHoursFromNow)
            
        forecastDiff = int((forecastTime - downloadTime).seconds / 3600.0)
        if forecastDiff > 78:
            forecastDiff = int(math.floor(forecastDiff / 3.0) * 3.0)
        if forecastDiff > 180:
            forecastDiff = 180

        # Generate download URLs

        downloadURLs = {} 
        for variableID in ICON_VARIABLES:
            downloadURLs[variableID] = \
                self.__getURL(variableID, timeIdentifier, forecastDiff)
        downloadAndCompile(\
            downloadURLs, tempDir=self.tempDir, resourceDir=self.resourceDir)
        
