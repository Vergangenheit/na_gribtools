#!/usr/bin/env python3

import os
import yaml

class JoinablePath(str):

    def __init__(self, value):
        str.__init__(self)
        self.__value = value

    def __call__(self, *args):
        return os.path.join(self.__value, *args)


class ConfigParser:

    def __init__(self, path):
        self.__filepath = path
        self.__yaml = yaml.load(open(path, "r"))

        Path = lambda i: JoinablePath(os.path.realpath(i))
        self.resourceDir = Path(self.__yaml["resource"])
        self.workDir = Path(self.__yaml["workdir"])

        self.archiveLife = int(self.__yaml["archive-life"])
        self.checksumKey = self.__yaml["checksum-key"]

        assert self.archiveLife > 0
