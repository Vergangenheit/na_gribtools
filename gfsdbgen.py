#!/usr/bin/env python3

import sys
import os
import json
import subprocess
import numpy
import struct

from na_gribtools.metadata import *
from na_gribtools.raster import *
from na_gribtools.gfs.db import *

TARGET = sys.argv[1]

##############################################################################


#with GFSDatabase(TARGET, "w+") as db:
    #db.generate()
#    pass

with GFSDatabase(TARGET) as db:
    print(db.readByLatLng(42.167, 123.637))
