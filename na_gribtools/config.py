#!/usr/bin/env python3

import os
import yaml
from typing import Union, Dict, List


class JoinablePath(str):

    def __init__(self, value):
        str.__init__(self)
        self.__value = value

    def __call__(self, *args) -> str:
        return os.path.join(self.__value, *args)


class ConfigParser:

    def __init__(self, path):
        self.__filepath = path
        self.__yaml: Union[Dict, List, None] = yaml.load(open(path, "r"), Loader=yaml.FullLoader)

        Path = lambda i: JoinablePath(os.path.realpath(i))
        self.resourceDir: JoinablePath = Path(self.__yaml["resource"])
        self.workDir: JoinablePath = Path(self.__yaml["workdir"])

        self.archiveLife: int = int(self.__yaml["archive-life"])
        self.checksumKey: List = self.__yaml["checksum-key"]

        assert self.archiveLife > 0
