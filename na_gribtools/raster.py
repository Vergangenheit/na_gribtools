#!/usr/bin/env python3

import struct
import gdal
from gdalconst import *
import math

class RasterDataReader:

    def __init__(self, filename):
        self.__g = gdal.Open(filename, GA_ReadOnly)
        if not self.__g:
            raise Exception("Cannot read this file.")
        self.transform = self.__g.GetGeoTransform()
        self.bandsCount = self.__g.RasterCount
        self.xSize = self.__g.RasterXSize
        self.ySize = self.__g.RasterYSize
        self.shape = (self.ySize, self.xSize)

    def __getRectFromLatLng(self, lat, lng):
        """Reverse transform from lat/lng coordinates to X-Y.
            lng = TOPLEFTX + (x + 1) * RESX, x starts from 0
            lat = TOPLEFTY + (y + 1) * RESY, y starts from 0
        """
        TOPLEFTX, RESX, _, TOPLEFTY, __, RESY = self.transform
        x = math.floor((lng - TOPLEFTX) / RESX - 1) + 1
        y = math.floor((lat - TOPLEFTY) / RESY - 1) + 1
        print(self.transform, lat, lng, x, y)
        return (x, y, 1, 1) # left, top, x-size, y-size

    def getLatLngFromXY(self, x, y):
        TOPLEFTX, RESX, _, TOPLEFTY, __, RESY = self.transform
        lat = TOPLEFTY + (y + 1) * RESY
        lng = TOPLEFTX + (x + 1) * RESX
        return lat, lng

    def __unpackData(self, data, dataType):
        dataTypeName = gdal.GetDataTypeName(dataType)
        unpacker = {
            "Float64": ("d", lambda c: int(len(c)/8)),
            "Float32": ("f", lambda c: int(len(c)/4)),
        }
        if not dataTypeName in unpacker:
            raise Exception("%s cannot be converted yet." % dataTypeName)
        char, counter = unpacker[dataTypeName]
        return struct.unpack(char * counter(data), data)

    def dumpBand(self, band):
        band = self.__g.GetRasterBand(band)
        data = band.ReadAsArray(0, 0, self.xSize, self.ySize) 
        return data # array[ySize][xSize]

    def dumpBandLine(self, band, y):
        band = self.__g.GetRasterBand(band)
        data = band.ReadAsArray(0, y, self.xSize, 1) 
        return data[0] # [xSize]

    def readBand(self, band, lat, lng):
        assert band <= self.bandsCount and band >= 1
        left, top, xsize, ysize = self.__getRectFromLatLng(lat, lng)
        
        band = self.__g.GetRasterBand(band)
        data = band.ReadRaster(left, top, xsize, ysize, buf_type=band.DataType)
        data = self.__unpackData(data, band.DataType)

        return data

