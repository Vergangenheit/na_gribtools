#!/usr/bin/env python3

import os
import sys
import subprocess
import datetime
import math
import re

from .variables import *
from .dbcache import *

DATASET_DELAY = datetime.timedelta(hours=3)



class ICONDatabase:

    def __init__(self, config): 
    # tempDir="/tmp/na_dwd/", resourceDir="./resources/"):
        self.resourceDir = config.resourceDir
        self.tempDir = config.workDir

    def __getDatasetFilename(\
        self, variableID, timeIdentifier, hours, ending=".grib2.bz2"
    ):
        vName, vLevel, vBand = ICON_VARIABLES[variableID]
        return "ICON_iko_%s_elements_world_%s_%s_%03d%s" % (\
            vLevel,
            vName.upper(),
            timeIdentifier,
            hours,
            ending
        )

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
        URL += self.__getDatasetFilename(\
            variableID, timeIdentifier, hours, ".grib2.bz2")
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

        forecastDiff = int((forecastTime - downloadTime).total_seconds() / 3600.0)
        if forecastDiff > 78:
            forecastDiff = int(math.floor(forecastDiff / 3.0) * 3.0)
        if forecastDiff > 180:
            forecastDiff = 180

        # Generate download URLs

        downloadURLs = {} 
        for variableID in ICON_VARIABLES:
            downloadURLs[variableID] = \
                self.__getURL(variableID, timeIdentifier, forecastDiff)

        return downloadAndCompile(\
            timeIdentifier, forecastDiff, downloadURLs,
            tempDir=self.tempDir, resourceDir=self.resourceDir)

    def listDatabase(self):
        ret = {}

        for name in os.listdir(self.tempDir):
            fullpath = os.path.join(self.tempDir, name)

            # filter
            if not os.path.isfile(fullpath): continue
            if not fullpath.endswith(".icondb"): continue
            
            # parse timestamp
            match = re.search("([0-9]{10})_([0-9]{3})", name)
            if not match: continue
            try:
                runTime = timeIdentifierToDatetime(match.group(1))
                forecastHours = int(match.group(2))
                forecastTime = runTime + \
                    datetime.timedelta(hours=forecastHours)
            except:
                continue

            # list
            ret[(runTime, forecastHours)] = {
                "path": fullpath,
                "runtime": runTime,
                "forecasttime": forecastTime,
                "forecasthours": forecastHours,
            }

        return ret

    def cleanUp(self, beforeHours=9):
        """Delete files whose run time is older as `beforeHours`."""
        assert type(beforeHours) == int and beforeHours > 0
        now = datetime.datetime.utcnow()
        delList = []
        for name in os.listdir(self.tempDir):
            fullpath = os.path.join(self.tempDir, name)

            # filter
            if not os.path.isfile(fullpath): continue
            want = False
            for suffix in [".icondb", ".grb2", ".grib2", ".grib2.bz2"]:
                if fullpath.endswith(suffix):
                    want = True
                    break
            if not want: continue
            
            # parse timestamp
            match = re.search("([0-9]{10})_[0-9]{3}", name)
            if not match: continue
            try:
                runTime = timeIdentifierToDatetime(match.group(1))
            except:
                # if even the run time of a seemingly dataset could not be
                # parsed, then delete it.
                delList.append(fullpath)
                continue

            if (now - runTime).total_seconds() > beforeHours * 3600:
                delList.append(fullpath)
        for each in delList:
            print("Delete: %s" % each)
            os.unlink(each)


    def getSingleForecast(self, timestamp, forecastDiff):
        assert type(forecastDiff) == int
        if isinstance(timestamp, datetime.datetime):
            timestamp = "%04d%02d%02d%02d" % (
                timestamp.year,
                timestamp.month,
                timestamp.day,
                timestamp.hour
            )
        assert type(timestamp) == str

        filepath = getICONDBPath(self.tempDir, timestamp, forecastDiff)
        if not os.path.isfile(filepath):
            return None
        return ICONDBReader(filepath)
