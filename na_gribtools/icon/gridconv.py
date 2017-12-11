#!/usr/bin/env python3

import subprocess
import os

def convertDWDGrid(resourceDir, inputFile, removeOnSuccess=True):
    if not os.path.isdir(resourceDir):
        raise Exception("Resource file directory doesn't exist.")

    resFile = lambda i: os.path.realpath(os.path.join(resourceDir, i))
    targetFile = resFile("target_grid_world_0125.txt")
    weightFile = resFile("weights_icogl2world_0125.nc")

    if not (os.path.isfile(targetFile) and os.path.isfile(weightFile)):
        raise Exception("One or more expected file(s) cannot be accessed:\n" +\
            " 1. %s\n 2. %s\n\n" % (targetFile, weightFile) + \
            "Please download them from " + \
            "https://opendata.dwd.de/weather/lib/ICON_GLOBAL2WORLD_0125_EASY.tar.bz2"
        )

    if not os.path.isfile(inputFile):
        raise Exception("Input file doesn't exist.")

    try:
        if inputFile.endswith(".grb2"):
            return inputFile
        elif inputFile.endswith(".grib2"):
            outputFile = inputFile[:-6] + ".grb2"
        elif inputFile.endswith(".grib2.bz2"):
            outputFile = inputFile[:-10] + ".grb2"
            subprocess.check_output(["bunzip2", inputFile])
            inputFile = inputFile[:-4]
        else:
            raise Exception("Input must be a .grib2 or .grib2.bz2 file.")

        outputFileTemp = outputFile + ".temp"
        command = [\
            "cdo", "-f", "grb2", "remap,%s,%s" % (targetFile, weightFile), \
            inputFile, outputFileTemp
        ]
        subprocess.check_output(command)
        subprocess.check_output(["mv", outputFileTemp, outputFile])
        assert os.path.isfile(outputFile)
    except Exception as e:
        raise e

    try:
        os.chmod(outputFile, 0o644)
        if removeOnSuccess:
            os.unlink(inputFile)
    except:
        pass

    return outputFile


if __name__ == "__main__":
    import sys
    if len(sys.argv) != 3:
        print("Usage: python3 gridconv.py <Resource Dir> <Input File>")
        exit(1)

    convertDWDGrid(sys.argv[1], sys.argv[2])
