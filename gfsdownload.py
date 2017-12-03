#!/usr/bin/env python3

from na_gribtools.gfs.download import *

tasks = GFSDownloadTasks()

open("latest.txt", "w+").write(tasks.checkLatestFiles())
