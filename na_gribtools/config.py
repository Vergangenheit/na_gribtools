#!/usr/bin/env python3

import os
import yaml

class ConfigParser:

    def __init__(self, path):
        self.__filepath = path
        self.__yaml = yaml.load(open(path, "r"))

        self.resourceDir = os.path.realpath(self.__yaml["resource"])
        self.workDir = os.path.realpath(self.__yaml["workdir"])
        self.archiveLife = int(self.__yaml["archive-life"])
        self.checksumKey = self.__yaml["checksum-key"]

        assert self.archiveLife > 0
