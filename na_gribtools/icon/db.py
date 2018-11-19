#!/usr/bin/env python3

import os
import sys
import subprocess
import datetime
import math
import re

from .variables import *
from .dbcache import *
from ..filesystem import *

DATASET_DELAY = datetime.timedelta(hours=3)



class ICONDatabase:

    def __init__(self, config): 
        self.resourceDir = config.resourceDir
        self.tempDir = config.workDir
        self.archiveLife = config.archiveLife
        self.checksumKey = config.checksumKey

    def __getDatasetFilename(\
        self, variableID, timeIdentifier, hours, ending=".grib2.bz2"
    ):
        #icon_global_icosahedral_single-level_2018111900_000_ALB_RAD.grib2.bz2
        vName, vLevel, vBand = ICON_VARIABLES[variableID]
        return "icon_global_icosahedral_%s_%s_%03d_%s%s" % (
            vLevel.lower(),
            timeIdentifier,
            hours,
            vName.upper(),
            ending
        )
        """return "ICON_iko_%s_elements_world_%s_%s_%03d%s" % (\
            vLevel,
            vName.upper(),
            timeIdentifier,
            hours,
            ending
        )"""

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
        #https://opendata.dwd.de/weather/nwp/icon/grib/00/alb_rad/icon_global_icosahedral_single-level_2018111900_000_ALB_RAD.grib2.bz2
        URL = "https://opendata.dwd.de/weather/nwp/icon/grib/"
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

    def __downloadAndCompile(self, timeIdentifier, hours):
        """Generate instructions for downloader function and finally call
        it."""
        downloadURLs = {} 

        for variableID in ICON_VARIABLES:
            downloadURLs[variableID] = \
                self.__getURL(variableID, timeIdentifier, hours)

        return downloadAndCompile(\
            timeIdentifier, hours, downloadURLs,
            tempDir=self.tempDir,
            resourceDir=self.resourceDir,
            checksumKey=self.checksumKey
        )

    def downloadForecastFromRuntime(self, forecastHoursFromRuntime=1):
        timeIdentifier, downloadTime = self.__getDownloadTimeInfo()
        try:
            assert type(forecastHoursFromRuntime) == int
            assert forecastHoursFromRuntime in range(1, 181)
            if forecastHoursFromRuntime > 78:
                assert forecastHoursFromRuntime % 3 == 0
        except:
            raise Exception("Requested forecast hour invalid.")
        return self.__downloadAndCompile(\
            timeIdentifier, forecastHoursFromRuntime)

    def downloadForecastFromNow(self, forecastHoursFromNow=6):
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

        return self.__downloadAndCompile(timeIdentifier, forecastDiff)

    def listGRB2ForImages(self):
        """List and parse all .grb2 original files in archive directory.
        
        Returns: a list, each item is a dict containing:
            * path: the full path to given .grb2 file.
            * config: 
        """
        ret = []
        gribArchives = filterDirWithSuffix(self.tempDir, [".grb2"])
        for fullpath in gribArchives:
            filename = os.path.split(fullpath)[-1]
            try:
                match = re.search("([0-9]{10})_([0-9]{3})", filename)
                runTime = timeIdentifierToDatetime(match.group(1))
                forecastHours = int(match.group(2))
                forecastTime = \
                    runTime + datetime.timedelta(hours=forecastHours)
            except:
                continue
            # check if this file might be an interested image output based on
            # definition from `na_gribtools/icon/variables.py`
            for interested in ICON_IMAGE_OUTPUT:
                varConfig = ICON_VARIABLES[interested]
                varName, varLevel, _ = varConfig
                if varName.upper() in filename and varLevel in filename:
                    ret.append({
                        "path": fullpath,
                        "item": interested,
                        "definition": varConfig,
                        "config": ICON_IMAGE_OUTPUT[interested],
                        "runtime": runTime,
                        "forecast": forecastTime,
                    })
        return ret

    def listDatabase(self):
        ret = {} 

        for name in os.listdir(self.tempDir):
            fullpath = os.path.join(self.tempDir, name)

            # filter
            if not fullpath.endswith(".icondb"): continue
            if not os.path.isfile(fullpath): continue
            
            # parse timestamp
            match = re.search("forecast-([0-9]{10})", name)
            if not match: continue
            try:
                timeIdentifier = match.group(1)
                forecastTime = timeIdentifierToDatetime(timeIdentifier)
            except:
                continue

            # list
            ret[timeIdentifier] = {
                "path": fullpath,
                "forecasttime": forecastTime,
            }

        return ret

    def cleanUp(self):
        """Delete files whose run time is older as `beforeHours`."""
        now = datetime.datetime.utcnow()
        archiveLifeDelta = datetime.timedelta(hours=self.archiveLife)
        oneHourDelta = datetime.timedelta(hours=1)

        deleteArchiveWithRunTimeBefore = now - archiveLifeDelta
        deleteICONDBWithForecastTimeBefore = now - oneHourDelta

        isOlderThan = lambda a,b: (b-a).total_seconds() > 0 # a is older than b

        delList = []

        # delete grib archives
        
        gribArchives = filterDirWithSuffix(
            self.tempDir, 
            [".grb2", ".grib2", ".grib2.bz2"]
        )
        for path in gribArchives:
            filename = os.path.split(path)[-1]
            match = re.search("([0-9]{10})_[0-9]{3}", filename)
            try:
                runTime = timeIdentifierToDatetime(match.group(1))
                if isOlderThan(runTime, deleteArchiveWithRunTimeBefore):
                    delList.append(path)
            except:
                # if even the run time of a seemingly dataset could not be
                # parsed, then delete it.
                delList.append(path)
                continue

        # delete old icondb files

        icondbFiles = filterDirWithSuffix(
            self.tempDir, [".icondb", ".icondb.temp", ".png", ".tiff"])
        for path in icondbFiles:
            filename = os.path.split(path)[-1]
            match = re.search("\\-([0-9]{10})\\.", filename)
            if not match: continue
            try:
                runTime = timeIdentifierToDatetime(match.group(1))
                if isOlderThan(runTime, deleteICONDBWithForecastTimeBefore):
                    delList.append(path)
            except:
                # if even the run time of a seemingly dataset could not be
                # parsed, then delete it.
                delList.append(path)
                continue
            
        for each in delList:
            print("Delete: %s" % each)
            os.unlink(each)


    def getSingleForecast(self, timestamp):
        assert type(timestamp) == str
        filepath = getICONDBPath(self.tempDir, timestamp)
        if not os.path.isfile(filepath):
            return None
        return ICONDBReader(filepath)
