#!/usr/bin/env python3

"""
`na_gribtools` specific cached data file
========================================

2 functions are provided here:
    * downloadAndCompile
    *

# downloadAndCompile

is a function for downloading several dataset from DWD's server and compiling
them into a data file used by this library.

The data file begins with 2 byte little-endian length mark, indicating the
header's length that follows up. The header itself is JSON and may be parsed.

Immediately after header there's data packed. Each piece of data comprises a
length of 8x(number_of_variables+2) bytes, where all interested variables are
listed in `variables.py`, and the first 16 bytes reserved for the 2 double
values of latitude & longitude.

For example, if 2 variables: `t_2m` and `tot_prec` are listed, a piece of data
will be 4x8=32 bytes: <latitude, longitude, t_2m, tot_prec>.

The pieces are written in file per column(x) and per row(y) as the same
sequence in grib file:

    <x=0, y=0>, <x=1, y=0>, ......<x=2879, y=0>
    <x=0, y=1>...
    ...

so that on reading this file it would be easy if (x,y) can be calculated with
known geo-transformation(which will be recorded in header): just seek to
(y*xSize + x) * bytes_per_entry and read.

"""


import os
import sys
import subprocess
import struct
import json
import re

from .variables import *
from .gridconv import *
from ..raster import *
from ..timeidentifier import *

ICONDB_VARIABLES_PER_ENTRY = 2 + len(ICON_VARIABLE_INDEXES)

# use double float
"""ICONDB_SINGLE_VARIABLE_PACKER = "<d"
ICONDB_SINGLE_VARIABLE_BYTES_SIZE = 8
ICONDB_VARIABLES_PACKER = "<" + "d" * ICONDB_VARIABLES_PER_ENTRY"""

# use single float
ICONDB_SINGLE_VARIABLE_PACKER = "<f"
ICONDB_SINGLE_VARIABLE_BYTES_SIZE = 4
ICONDB_VARIABLES_PACKER = "<" + "f" * ICONDB_VARIABLES_PER_ENTRY

ICONDB_ENTRY_BYTES_SIZE = \
    ICONDB_SINGLE_VARIABLE_BYTES_SIZE * ICONDB_VARIABLES_PER_ENTRY


##############################################################################
# General functions

def getICONDBPath(tempDir, timeIdentifier, forecastHours):
    return os.path.join(tempDir,
        "%s_%03d.icondb" % (timeIdentifier, forecastHours)
    )


##############################################################################
# Downloading and compiling function

def __downloadByInstructions(instructions, tempDir):
    # returns a map from variableID to local file path
    ret = {}
    cmds = []
    for variableID in instructions:
        filename = instructions[variableID].split("/")[-1]
        fullpath = os.path.join(tempDir, filename)
        alternativePath = fullpath[:-10] + ".grb2"
        if os.path.isfile(alternativePath):
            ret[variableID] = alternativePath 
        else:
            ret[variableID] = fullpath
            if not os.path.isfile(fullpath):
                cmds.append(instructions[variableID])
    if cmds:
        p = subprocess.Popen(\
            ["wget", "-P", tempDir, "-i", "-"], stdin=subprocess.PIPE)
        cmd = "\n".join(cmds)
        p.communicate(input=cmd.encode("utf-8"))
    for each in ret:
        if not os.path.isfile(ret[each]): return None
    return ret

def downloadAndCompile(\
    timeIdentifier, forecastDiff, instructions,
    resourceDir="./resource", tempDir="/tmp/"
):
    """`instructions` must be a dict of variableID=>URL"""

    # Download Files

    i = 0
    while i < 3:
        downloadedFiles = __downloadByInstructions(instructions, tempDir)
        if downloadedFiles:
            break  
        i += 1
    if not downloadedFiles:
        raise Exception("One or more files cannot be downloaded.")
    for variableID in downloadedFiles:
        downloadedFiles[variableID] = convertDWDGrid(
            resourceDir, downloadedFiles[variableID], True)

    # Compile files into a large db file
    
    outputFile = getICONDBPath(tempDir, timeIdentifier, forecastDiff)

    print("Output set to: %s" % outputFile)

    with open(outputFile, "wb+") as f:
        
        # ---- create file

        print("Creating an empty output file...")
        
        rasterSet = []
        for variableID in ICON_VARIABLE_INDEXES:
            rasterSet.append((\
                RasterDataReader(downloadedFiles[variableID]),
                *ICON_VARIABLES[variableID]
            )) # rasterReader, name, level, band

        print("Recording metadata...")

        xSize, ySize = rasterSet[0][0].xSize, rasterSet[0][0].ySize
        transform = rasterSet[0][0].transform

        metadataBin = json.dumps({
            "time": timeIdentifier,
            "forecast": forecastDiff,
            "xSize": xSize,
            "ySize": ySize,
            "transform": transform,
        }).encode("utf-8")

        metadataBinLength = len(metadataBin)

        f.seek(0, os.SEEK_SET)
        f.write(struct.pack("<H", metadataBinLength)) # which takes 2 bytes
        f.write(metadataBin)

        headerLength = metadataBinLength + 2

        print("Recording data...")

        for y in range(0, ySize):
            xDataSet = [
                raster.dumpBandLine(band, y)\
                for raster, name, level, band in rasterSet]
            for x in range(0, xSize):
                lat, lng = rasterSet[0][0].getLatLngFromXY(x, y)
                xData = [each[x] for each in xDataSet]
                f.write(struct.pack(
                    ICONDB_VARIABLES_PACKER,
                    lat, lng, *xData
                ))

        """
        # ---- read raster data and dump into file

        # first 2 positions for lat & lng
        perEntryOffset = 2 * ICONDB_SINGLE_VARIABLE_BYTES_SIZE

        for variableID in ICON_VARIABLE_INDEXES:
            # deal with this file specified by variableID

            print("Dumping raster: %s" % variableID)
            
            name, level, band = ICON_VARIABLES[variableID]
            raster = RasterDataReader(downloadedFiles[variableID])
            f.seek(perEntryOffset + headerLength, os.SEEK_SET)
            
            for y in range(0, raster.ySize):
                xData = raster.dumpBandLine(band, y) # get a whole line, quick
                for x in range(0, raster.xSize):
                    buf = struct.pack(
                        ICONDB_SINGLE_VARIABLE_PACKER,
                        xData[x]
                    )
                    continue
                    f.write(buf)
                    f.seek(
                        ICONDB_ENTRY_BYTES_SIZE - ICONDB_SINGLE_VARIABLE_BYTES_SIZE,
                        os.SEEK_CUR
                    ) # skip to next

            perEntryOffset += ICONDB_SINGLE_VARIABLE_BYTES_SIZE
        """

    return outputFile


##############################################################################
# Extracting info from a cache db

class ICONDBReader:

    def __init__(self, filename):
        if not os.path.isfile(filename) or not filename.endswith(".icondb"):
            raise Exception("Not a ICON cached database.")

        with open(filename, "rb") as f:
            f.seek(0, os.SEEK_SET)
            metadataBinLength = struct.unpack("<H", f.read(2))[0]
            metadata = f.read(metadataBinLength)
            self.dataOffset = metadataBinLength + 2
            self.metadata = json.loads(metadata.decode("utf-8"))

        self.__filename = filename
        self.__xSize = self.metadata["xSize"]
        self.__ySize = self.metadata["ySize"]
        self.__timeIdentifier = self.metadata["time"]
        self.__forecastHours = self.metadata["forecast"]
        self.__transform = self.metadata["transform"]
        self.__runTime = timeIdentifierToDatetime(self.__timeIdentifier)
        self.__forecastTime =\
            self.__runTime + datetime.timedelta(hours=self.__forecastHours)
        
    def __enter__(self, *args, **argv):
        self.__f = open(self.__filename, "rb")
        return self

    def __exit__(self, *args, **argv):
        self.__f.close()

    def query(self, lat, lng):
        x, y = geotransformLatLngToXY(self.__transform, lat, lng)
        offset = self.dataOffset +\
            (y * self.__xSize + x) * ICONDB_ENTRY_BYTES_SIZE
        self.__f.seek(offset, os.SEEK_SET)
        data = struct.unpack(
            ICONDB_VARIABLES_PACKER,
            self.__f.read(ICONDB_ENTRY_BYTES_SIZE))
        ret = {
            "lat": data[0],
            "lng": data[1],
            "runtime": self.__runTime,
            "forecast": self.__forecastTime,
        }
        data = data[2:]
        for i in range(0, len(data)):
            variableID = ICON_VARIABLE_INDEXES[i]
            ret[variableID] = data[i]
        return ret
