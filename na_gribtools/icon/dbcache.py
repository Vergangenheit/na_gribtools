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
        alternativePath = fullpath[:-10] + ".grb2"
        if os.path.isfile(alternativePath):
            ret[variableID] = alternativePath 
        else:
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
    i = 0
    while i < 3:
        downloadedFiles = __downloadByInstructions(instructions, tempDir)
        if downloadedFiles:
            break  
        i += 1
    if not downloadedFiles:
        raise Exception("One or more files cannot be downloaded.")

    for variableID in downloadedFiles:
        downloadedFiles[variableID] = convertDWDGrid(
            resourceDir, downloadedFiles[variableID], True)

    
    print(downloadedFiles)
