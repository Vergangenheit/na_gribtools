#!/usr/bin/env python3

import os
import sys
import subprocess

from .variables import *
from .gridconv import *
from ..raster import *

def __downloadByInstructions(instructions, tempDir):
    # returns a map from variableID to local file path
    ret = {}
    cmds = []
    for variableID in instructions:
        filename = instructions[variableID].split("/")[-1]
        fullpath = os.path.join(tempDir, filename)
        ret[variableID] = fullpath
        if not os.path.isfile(fullpath):
            cmds.append(instructions[variableID])
    if cmds:
        p = subprocess.Popen(\
            ["wget", "-P", tempDir, "-i", "-"], stdin=subprocess.PIPE)
        cmd = "\n".join(cmds)
        p.communicate(input=cmd.encode("utf-8"))

    for each in ret:
        if not os.path.isfile(ret[each]): return None
    return ret

def downloadAndCompile(instructions, resourceDir="./resource", tempDir="/tmp/"):
    """`instructions` must be a dict of variableID=>URL"""
    downloadedFiles = __downloadByInstructions(instructions, tempDir)
    print(downloadedFiles)
