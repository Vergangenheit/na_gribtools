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


db = GFSDatabase(TARGET)

db.generate()
