#!/usr/bin/env python3

import sys
import os
import struct

from ..raster import *
from .variables import *

class GFSDatabase:

    def __init__(self, gfsFilename):
        if not gfsFilename.endswith(".grb2"):
            raise Exception("Requires a .grb2 file as input.")
        self.gfsFilename = gfsFilename
        self.dbFilename = self.gfsFilename + ".gfsdb"

    def generate(self):
        rasterReader = RasterDataReader(self.gfsFilename)
        with open(self.dbFilename, "wb+") as f:
            bandData = {}

            for y in range(0, rasterReader.ySize):
                # for each line
                print("Progress: %f %%" % (y / rasterReader.ySize * 100.0))

                # cache all data for this line

                for bandID in GFS_VARIABLE_INDEXES:
                    bandData[bandID] = rasterReader.dumpBandLine(bandID, y)

                # for each x point
                values = [0] * (2+GFS_VARIABLE_COUNT)
                packer = "<%s" % ("d" * (2+GFS_VARIABLE_COUNT))

                for x in range(0, rasterReader.xSize):
                    values[0], values[1] = rasterReader.getLatLngFromXY(x, y)
                    valueCursor = 2
                    
                    for bandID in GFS_VARIABLE_INDEXES:
                        values[valueCursor] = bandData[bandID][x]
                        valueCursor += 1

                    f.write(struct.pack(packer, *values))
