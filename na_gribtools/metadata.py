#!/usr/bin/env python3

import sys
import os
import json
import subprocess


def getMetadata(filename):
    try:
        assert os.path.isfile(filename)
        assert filename.endswith(".grib") or filename.endswith(".grib2") \
               or filename.endswith(".grb2")
    except:
        raise Exception("Input might not be a GRIB file.")

    cacheFilename = filename + ".metadata"
    if os.path.isfile(cacheFilename):
        try:
            return json.loads(open(cacheFilename, "r").read())
        except:
            print("Generate metadata cache...")

    try:
        rawMetadata = subprocess.check_output( \
            ["gdalinfo", "-json", TARGET]
        ).decode("ascii")
        try:
            open(cacheFilename, "w+").write(rawMetadata)
        except:
            print("Unable to generate cache.")
        return json.loads(rawMetadata)
    except:
        return None
