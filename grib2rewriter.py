#!/usr/bin/env python3

import sys
import os
import json
import subprocess

from na_gribtools.metadata import *
from na_gribtools.raster import *

##############################################################################

TARGET = sys.argv[1]
LAT, LNG = (53, 16)

VARIABLES = [
    
]


##############################################################################

metadata = getMetadata(TARGET)
rasterReader = RasterDataReader(TARGET)

ret = {}

for band in metadata["bands"]:
    bandID = band["band"]
    bandMetadata = band["metadata"][""]

    variableName = bandMetadata["GRIB_ELEMENT"]
    if variableName not in VARIABLES: continue
    ret[variableName] = rasterReader.readBand(bandID, LAT, LNG)[0]

print(ret)
