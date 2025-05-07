from os import getcwd, path, mkdir
from time import time

class LogFile:
    def __init__(self, fpath =  "logs"):
        if not path.exists(fpath):
            mkdir(fpath)
        self.file = open(path.join(getcwd(), fpath, f"{time()}.csv"), "w+")

