#!/usr/bin/env python3

import sys
import os
import struct

from ..raster import *
from ..metadata import getMetadata
from .variables import *


VARIABLES_PER_ENTRY = 2 + GFS_VARIABLE_COUNT
VARIABLES_PACKER = "<" + "d" * VARIABLES_PER_ENTRY
ENTRY_BYTES_SIZE = 8 * VARIABLES_PER_ENTRY


class GFSDatabase:

    def __init__(self, gfsFilename):
        if not gfsFilename.endswith(".grb2"):
            raise Exception("Requires a .grb2 file as input.")
        self.gfsFilename = gfsFilename
        self.dbFilename = self.gfsFilename + ".gfsdb"
        
    def __buildReturnData(self, array):
        lat, lng = array[:2]
        array = array[2:]
        ret = {"lat": lat, "lng": lng}
        for i in range(0, GFS_VARIABLE_COUNT):
            variableID = GFS_VARIABLE_INDEXES[i]
            variableDesc = GFS_VARIABLES[variableID][2]
            variableName = GFS_VARIABLES[variableID][1] + ":" + GFS_VARIABLES[variableID][0]

            ret[variableName] = {
                "name": variableName,
                "value": array[i],
                "desc": variableDesc,
            }
        return ret

    def __enter__(self):
        if not os.path.isfile(self.dbFilename):
            self.__generate()

        self.__f = open(self.dbFilename, "rb")
        return self

    def __exit__(self, *args, **argv):
        self.__f.close()
        del self.__f

    def readByLatLng(self, lat, lng):
        rasterReader = RasterDataReader(self.gfsFilename)

        if not ( \
            -90 < lat and lat < 90 and \
            -180 < lng and lng < 180
        ):
            raise Exception("Invalid latitude or longitude.")
        if lng < 0: lng += 360

        x, y = rasterReader.getXYFromLatLng(lat, lng)
        return self.readByXY(x, y)
        

    def readByXY(self, x, y):
        rasterReader = RasterDataReader(self.gfsFilename)

        if not (
            x >= 0 and x < rasterReader.xSize\
            and y >= 0 and y < rasterReader.ySize
        ):
            raise Exception("Invalid x or y range.")
            
        offset = (y * rasterReader.xSize + x) * ENTRY_BYTES_SIZE

        try:
            self.__f.seek(offset, 0)
            data = self.__f.read(ENTRY_BYTES_SIZE)
            data = struct.unpack(VARIABLES_PACKER, data)
            return self.__buildReturnData(data)
        except Exception as e:
            print(e)
            return None


    def __generate(self):
        rasterReader = RasterDataReader(self.gfsFilename)
        bandData = {}

        with open(self.dbFilename, "wb+") as f:
            for y in range(0, rasterReader.ySize):
                # for each line
                print("Progress: %f %%" % (y / rasterReader.ySize * 100.0))

                # cache all data for this line

                for bandID in GFS_VARIABLE_INDEXES:
                    bandData[bandID] = rasterReader.dumpBandLine(bandID, y)

                # for each x point
                values = [0] * VARIABLES_PER_ENTRY

                for x in range(0, rasterReader.xSize):
                    values[0], values[1] = rasterReader.getLatLngFromXY(x, y)
                    valueCursor = 2
                    
                    for bandID in GFS_VARIABLE_INDEXES:
                        values[valueCursor] = bandData[bandID][x]
                        valueCursor += 1

                    f.write(struct.pack(VARIABLES_PACKER, *values))
