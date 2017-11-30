#!/usr/bin/env python3

import sys
import os
import json
import subprocess

TARGET = sys.argv[1]

def getMetadata(filename):
    cacheFilename = filename + ".metadata"
    if os.path.isfile(cacheFilename):
        try:
            return json.loads(open(cacheFilename, "r").read())
        except:
            print("generate metadata cache...")
    
    try:
        rawMetadata = subprocess.check_output(\
            ["gdalinfo", "-json", TARGET]
        ).decode("ascii")
        try:
            open(cacheFilename, "w+").write(rawMetadata)
        except:
            print("Unable to generate cache.")
        return json.loads(rawMetadata)
    except:
        return None


print(getMetadata(TARGET))
