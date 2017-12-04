#!/usr/bin/env python3

import os
import sys
import subprocess
import struct

from .variables import *
from .gridconv import *
from ..raster import *

ICONDB_VARIABLES_PER_ENTRY = 2 + len(ICON_VARIABLE_INDEXES)
ICONDB_SINGLE_VARIABLE_PACKER = "<d"
ICONDB_SINGLE_VARIABLE_BYTES_SIZE = 8
ICONDB_VARIABLES_PACKER = "<" + "d" * ICONDB_VARIABLES_PER_ENTRY
ICONDB_ENTRY_BYTES_SIZE = \
    ICONDB_SINGLE_VARIABLE_BYTES_SIZE * ICONDB_VARIABLES_PER_ENTRY


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
    
    outputFile = os.path.join(tempDir,
        "%s_%03d.icondb" % (timeIdentifier, forecastDiff)
    )

    print("Output set to: %s" % outputFile)

    with open(outputFile, "wb+") as f:
        
        # ---- create file

        print("Creating an empty output file...")
        
        raster = RasterDataReader(downloadedFiles[variableID])
        for y in range(0, raster.ySize):
            for x in range(0, raster.xSize):
                lat, lng = raster.getLatLngFromXY(x, y)
                f.write(struct.pack(
                    ICONDB_VARIABLES_PACKER,
                    lat, lng, *[0 * (ICONDB_VARIABLES_PER_ENTRY-2)]
                ))
    
        # ---- read raster data and dump into file

        # first 2 positions for lat & lng
        perEntryOffset = 2 * ICONDB_SINGLE_VARIABLE_BYTES_SIZE

        for variableID in ICON_VARIABLE_INDEXES:
            # deal with this file specified by variableID

            print("Dumping raster: %s" % variableID)
            
            name, level, band = ICON_VARIABLES[variableID]
            raster = RasterDataReader(downloadedFiles[variableID])
            f.seek(perEntryOffset, os.SEEK_SET) # to file begin, with offset
            
            for y in range(0, raster.ySize):
                xData = raster.dumpBandLine(band, y) # get a whole line, quick
                for x in range(0, raster.xSize):
                    buf = struct.pack(
                        ICONDB_SINGLE_VARIABLE_PACKER,
                        xData[x]
                    )
                    f.write(buf)
                    f.seek(
                        ICONDB_ENTRY_BYTES_SIZE - ICONDB_SINGLE_VARIABLE_BYTES_SIZE,
                        os.SEEK_CUR
                    ) # skip to next

            perEntryOffset += ICONDB_SINGLE_VARIABLE_BYTES_SIZE


    print(downloadedFiles)
