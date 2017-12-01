#!/usr/bin/env python3

# see below for definitions
#  http://www.nco.ncep.noaa.gov/pmb/products/gfs/gfs.t00z.pgrb2.0p25.f006.shtml


GFS_VARIABLES = {
    281: ("2m",     "TMP",      "Temperature [K]"),
    282: ("2m",     "SPFH",     "Specific Humidity [kg/kg]"),
    283: ("2m",     "DPT",      "Dew Point Temperature [K]"),
    284: ("2m",     "RH",       "Relative Humditity [%]"),
    286: ("2m",     "TMAX",     "Maximum Temperature [K]"),
    287: ("2m",     "TMIN",     "Minimum Temperature [K]"),

    293: ("0m",     "APCP",     "Total Precipitation [kg/m^2]"),
}

GFS_VARIABLE_INDEXES = sorted(GFS_VARIABLES.keys())

GFS_VARIABLE_COUNT = len(GFS_VARIABLE_INDEXES)
