#!/usr/bin/env python3

"""Provides useful filesystem operations."""

import os

def filterDirWithSuffix(path, suffix=[], fileOnly=True):
    dirlist = os.listdir(path)
    wanted = []
    for filename in dirlist:
        fullpath = os.path.realpath(os.path.join(path, filename))
        if fileOnly and not os.path.isfile(fullpath): continue
        for s in suffix:
            if filename.endswith(s):
                wanted.append(fullpath)
    return wanted
