#!/usr/bin/env python3
# encoding: utf-8

import logging, os

class Logger:
    def __init__(self, path, clever=logging.DEBUG, Flevel=logging.DEBUG):
        self.logger = logging.getLogger(path)
        self.logger.setLevel(logging.DEBUG)
        log_format = logging.Formatter('[%(asctime)s] [%(levelname)s] %(message)s', '%Y-%m-%d %H:%M:%S')
        fh = logging.FileHandler(path)
        fh.setFormatter(log_format)
        fh.setLevel(Flevel)
        self.logger.addHandler(fh)

    def debug(self, message):
        self.logger.debug(message)

    def info(self, message):
        self.logger.info(message)

    def infoPrint(self, mesage):
        print (mesage)
        self.logger.info(mesage)

    def war(self, message):
        self.logger.warn(message)

    def error(self, message):
        self.logger.error(message)

    def cri(self, message):
        self.logger.critical(message)


loggermap = {}
def getLocalLogger():
    logPath ="./log/"
    logName="info.log"
    isExists=os.path.exists(logPath)
    if not isExists:
        os.makedirs(logPath)
    if logPath+logName in loggermap:
        return loggermap[logPath+logName]
    else:
        logger = Logger(logPath+logName, logging.INFO, logging.INFO)
        loggermap[logPath+logName] = logger
        return logger

if __name__ == '__main__':
    log = getLocalLogger()
    log.info("vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv")