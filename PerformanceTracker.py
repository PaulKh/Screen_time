
import logging
import time

log = logging.getLogger("APP." + __name__)
class PerformaceTracker(object):
    tracker_name: str
    start_time : float
    def __init__(self, tracker_name):
        self.tracker_name = tracker_name
     
    def __enter__(self):
        self.start_time = time.time() 
        return True
 
    def __exit__(self, *args):
        log.debug(f"{self.tracker_name} calculation took {round(time.time()  - self.start_time, 5)} seconds")