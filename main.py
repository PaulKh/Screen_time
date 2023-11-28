import argparse
import logging
import os
import time
import traceback
from PerformanceTracker import PerformaceTracker
from logger_setup import setup_logger
from monitoring import Monitoring
import Quartz
import Constants

#Request youtube video details
# https://developers.google.com/youtube/v3/docs/videos/list?apix_params=%7B%22part%22%3A%5B%22snippet%2CcontentDetails%2Cstatistics%22%5D%2C%22id%22%3A%5B%22Ks-_Mh1QhMc%22%5D%7D
# Useful command to get process
# ps -jax | grep screen_time

def main():
    setup_logger("test_logs.log", logging.INFO, logging.INFO)
    logging.info("Starting application")
    log = logging.getLogger("APP." + __name__)

    parser = argparse.ArgumentParser(description='Configs file path')
    parser.add_argument('-f', '--file', dest='config_file',
                   help='Config file path', default="configs.cfg")
    configs_file = parser.parse_args().config_file
    monitoring = Monitoring()
    while True:
        with PerformaceTracker("got all urls"):
            try:
                d = Quartz.CGSessionCopyCurrentDictionary()
                if 'CGSSessionScreenIsLocked' not in d.keys():
                    #If screen is locked monitoring is not performed
                    monitoring.monitor(configs_file)
            except Exception as e:
                log.info(e)
                traceback.print_exc() 
        time.sleep(Constants.TICKER_TIME)

if __name__ == "__main__":
    main()
