#!/usr/bin/env python3
from typing import Tuple


def geotransformLatLngToXY(transform, lat: float, lng: float) -> Tuple[int, int]:
    """Reverse transform from lat/lng coordinates to X-Y.
        lng = TOPLEFTX + (x + 1) * RESX, x starts from 0
        lat = TOPLEFTY + (y + 1) * RESY, y starts from 0
    """
    TOPLEFTX, RESX, _, TOPLEFTY, __, RESY = transform
    realX: float = (lng - TOPLEFTX) / RESX - 1
    realY: float = (lat - TOPLEFTY) / RESY - 1
    x, y = round(realX), round(realY)
    return x, y


def geotransformXYToLatLng(transform, x, y):
    TOPLEFTX, RESX, _, TOPLEFTY, __, RESY = transform
    lat = TOPLEFTY + (y + 1) * RESY
    lng = TOPLEFTX + (x + 1) * RESX
    return lat, lng
