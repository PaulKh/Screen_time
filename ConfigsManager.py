from datetime import datetime
import json
import logging
import time
from typing import Optional

log = logging.getLogger("APP." + __name__)
class ConfigsManager():
    CONFIGS_FILENAME = "configs.cfg"

    __configs = {}

    def __init__(self, path_to_configs: str = CONFIGS_FILENAME):
        log.debug(f"Loading configs from {path_to_configs}")
        with open(path_to_configs) as json_file:
            self.__configs = json.load(json_file)

    def get_application_cfg(self, application_name: str) -> Optional[dict]:
        if "applications" in self.__configs:
            for application in self.__configs["applications"]:
                if application["application"] == application_name:
                    log.debug(f"Application {application_name} is in block list")
                    return application
        return None
    
    def is_full_release(self):
        if "full_release" in self.__configs: 
            start_time = self.__configs["full_release"]["start"]
            minutes_start_in_a_day = int(start_time[:-3]) * 60 + int(start_time[-2:])
            duration_minutes = self.__configs["full_release"]["duration"]
            now = datetime.now()
            minutes_since_midnight = (now - now.replace(hour=0, minute=0, second=0, microsecond=0)).total_seconds() / 60
            if minutes_since_midnight > minutes_start_in_a_day and minutes_since_midnight < minutes_start_in_a_day + duration_minutes:
                log.info("Full release is active")
                return True
        return False        

    def is_full_blackout(self):
        if "full_blackout" in self.__configs:
            start = self.__configs["full_blackout"]["start"]
            end = self.__configs["full_blackout"]["duration"] + start
            now = time.time()
            if now > start and now < end:
                return True
        return False
    
    def get_blacklisted_url(self, url: str) -> Optional[dict]:
        if "blacklist_urls" in self.__configs and url != None:
            for url_cfg in self.__configs["blacklist_urls"]:
                if url_cfg["full_domain_name"] and url_cfg["url"] in url:
                    log.debug(f"Url domain {url} is in black list")
                    return url_cfg
                # log.info(f"Url  {url}, url cfg {url_cfg['url']}")
                if url_cfg["full_domain_name"] == False and url_cfg["url"] == url:
                    log.debug(f"Url domain {url} is in black list")
                    return url_cfg
        return None
    
    def limit_reached(self, application_cfg: dict, application_name: str, value: float):
        if "limit" in application_cfg:
            if application_cfg["limit"] * 60 < value:
                log.debug(f"Application {application_name} limit is reached")
                return True
            return False
        else:
            # No limit, only time interval will be applied
            return False
    
    def is_in_whitelisted_urls(self, url: str):
        if "whitelist_urls" in self.__configs and url != None:
            if any(white_url in url for white_url in self.__configs["whitelist_urls"]):
                log.debug(f"Url {url} is in white list")
                return True
        return False
    
    def is_in_whitelisted_names(self, title: str):
        title_lower = title.lower()
        if "whitelist_names" in self.__configs:
            if any(white_name in title_lower for white_name in self.__configs["whitelist_names"]):
                log.debug(f"Name {title} is in white list")
                return True
        return False
    
    def is_within_time_limit(self, source_dict: dict, time_now: str):
        if "time_intervals" in source_dict:
            time_intervals = source_dict["time_intervals"]
            for interval in time_intervals:
                # log.info(f'{time_now} {interval["start"]} {interval["end"]} {time_now < interval["end"]} {interval["start"] < time_now}' )
                if interval["start"] < time_now and time_now < interval["end"]:
                    return True
        else:
            # There is no time interval defined -> no need to limit
            return True
        return False
            



