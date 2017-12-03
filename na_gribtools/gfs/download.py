#!/usr/bin/env python3

import re
import subprocess
import time

import requests


def fetch(url):
    return subprocess.check_output([
        "curl",
        "--max-time", "600",
        "--retry", "10",
        "--retry-max-time", "30",
        "--retry-delay", "5",
        url,
        "-H", "Pragma: no-cache",
        "-H", "User-Agent: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Ubuntu Chromium/62.0.3202.94 Chrome/62.0.3202.94 Safari/537.36",
        "-H", "Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
        "-H", "Referer: https://nomads.ncdc.noaa.gov/data/gfs4/"
    ]).decode("utf-8")

def findLatestFolder(url, pattern, s, e):
    try:
        output = fetch(url)
        found = []
        for each in re.findall(">%s\\/" % pattern, output):
            found.append(int(each[s:e]))
        if len(found) < 1: raise Exception()
        found.sort()
        return str(max(found))
    except:
        raise Exception("Cannot determine latest dataset.")


class GFSDownloadTasks:
    
    def __init__(self, url="https://nomads.ncdc.noaa.gov/data/gfs4/"):
        self.__urlBase = url

    def filterAvailableFiles(self, latestFileList):
        """Use self.checkLatestFiles() to get a list."""
        dirlistSplit = [i.strip() for i in dirlistRaw.split("\n") if i]
        print(dirlistSplit)

    def checkLatestFiles(self):
        self.latestYearMonth = findLatestFolder(\
            self.__urlBase,
            "2[0-9]{3}[0-1][0-9]",
            1, -1
        )
        self.latestDate = findLatestFolder(\
            self.__urlBase + "%s/" % self.latestYearMonth,
            "2[0-9]{3}[0-1][0-9][0-3][0-9]",
            1, -1
        )
        return fetch(self.__urlBase + "%s/%s/md5sum.%s" % (
            self.latestYearMonth, self.latestDate, self.latestDate
        ))
