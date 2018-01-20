#!/usr/bin/env python3
"""
Convert .grb2 file into an image based on predefined instructions.

`task` is a dict in format:
    {
        "path": fullpath,
        "item": interested,
        "definition": (DWD_offical_name, level, band_in_file),
        "config": ICON_IMAGE_OUTPUT[interested],        # for image output
        "runtime": runTime,
        "forecast": forecastTime,
    }
    see `na_gribtools/icon/db.py` for more information.

"""

import subprocess
import os
import sys
import json

from ..timeidentifier import * 
from .variables import *


_randomFilename = lambda i: os.urandom(32).hex() + "." + i

def _deleteFiles(l):
    for e in l: os.unlink(e)

def _rasterizeBorders(
    inputFilename,
    outputFilename,
    te=(-180, -90, 180, 90),
    t_srs="EPSG:4326",
    size=(2879,1441),
    color=(0, 0, 0)
):
    cmd = ["gdal_rasterize", "-ot", "Byte"]
    cmd += ["-te"] + [str(i) for i in list(te)]
    cmd += ["-a_srs", t_srs]
    cmd += [
        "-burn", str(color[0]),
        "-burn", str(color[1]),
        "-burn", str(color[2]),
        "-burn", "255",
    ]
    cmd += ["-ts", str(size[0]), str(size[1])]
    cmd += [inputFilename, outputFilename]
    print(" ".join(cmd))
    subprocess.check_output(cmd)
    return outputFilename


def _cropGeoTIFF(
    inputFilename,
    outputFilename,
    te=(-180, -90, 180, 90),
    t_srs="EPSG:4326",
    size=(2879,1441)
):
    # first, fix the coordinates provided by DWD .grb2 data
    try:
        cornerCoordinates = json.loads(
            subprocess.check_output(
                ["gdalinfo", "-json", inputFilename]).decode('utf-8')
        )["cornerCoordinates"]
        centerX, centerY = cornerCoordinates["center"]
    except:
        centerX, centerY = 359.875, 0 # cheatsheet value
    te = list(te)
    te[0] += centerX
    te[1] += centerY
    te[2] += centerX
    te[3] += centerY

    # generate command
    cmd = ["gdalwarp"]
    cmd += ["-te"] + [str(i) for i in te]
    cmd += ["-t_srs", t_srs]
    cmd += ["-ts", str(size[0]), str(size[1])]
    cmd += ["-r", "cubic"]
    cmd += [inputFilename, outputFilename]
    print(" ".join(cmd))
    subprocess.check_output(cmd)
    return outputFilename

def mergeGeoTIFFwithBorders(
    inputGeoTIFF, 
    outputFilename,
    bordersFilename="ne_10m_coastline.shp",
    te=(-180, -90, 180, 90),
    t_srs="EPSG:4326",
    size=(2879,1441),
    color=(0, 0, 0),
    config=None
):
    assert config != None
    tempDir = config.workDir

    cropFilename = tempDir(_randomFilename("tiff")) # raster data
    maskFilename = tempDir(_randomFilename("tiff")) # borders etc.

    try:
        _rasterizeBorders(
            config.resourceDir(bordersFilename), 
            maskFilename,
            te=te, size=size, color=color, t_srs=t_srs
        )
        _cropGeoTIFF(
            inputGeoTIFF,
            cropFilename,
            te=te, size=size, t_srs=t_srs
        )
        cmd = ["composite", maskFilename, cropFilename, outputFilename]
        subprocess.check_output(cmd)
        _deleteFiles([maskFilename, cropFilename])
        print("merged output: %s" % outputFilename)
        return outputFilename
    except Exception as e:
        print(e)


#-----------------------------------------------------------------------------

def doGRB2ToImageTask(task, config=None, forced=False):
    assert config != None

    inputName = task["item"]
    inputFile = task["path"]
    srcName, srcBand = task["definition"][0], task["definition"][2]
    outputConfig = task["config"]
    outputTimeIdentifier = datetimeToTimeIdentifier(task["forecast"])

    rasterFilename = config.workDir(
        "image-%s-%s.tiff" % (inputName, outputTimeIdentifier))

    workType = outputConfig["type"]

    if "color-relief" == workType:
        cmd = [ "gdaldem", "color-relief" ]
        if "gdaldem-options" in outputConfig:
            cmd += outputConfig["gdaldem-options"]
        cmd += [
            inputFile,
            config.resourceDir(outputConfig["color"]),
            rasterFilename
        ]
        subprocess.check_output(cmd)

        for regionName in ICON_IMAGE_REGIONS:
            regionDef, regionProj = ICON_IMAGE_REGIONS[regionName]
            
            outputFilenameTemp = config.workDir(
                "image-%s-%s.%s.temp.png" % (
                    inputName, outputTimeIdentifier, regionName
                )
            )
            if os.path.exists(outputFilenameTemp):
                os.unlink(outputFilenameTemp)
            outputFilename = outputFilenameTemp[:-9] + ".png"
            if not forced and os.path.exists(outputFilename): continue

            borderColor = (0, 0, 0)
            if "border-color" in outputConfig:
                borderColor = outputConfig["border-color"]

            try:
                mergeGeoTIFFwithBorders(
                    rasterFilename,
                    outputFilenameTemp,
                    config=config,
                    t_srs=regionProj,
                    te=regionDef,
                    size=ICON_IMAGE_SIZE,
                    color=borderColor
                )
                subprocess.check_output(
                    ["mv", outputFilenameTemp, outputFilename])
            except Exception as e:
                print(e)
    else:
        return
    
    subprocess.check_output(cmd)
