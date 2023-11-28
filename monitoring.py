#!/usr/bin/python
#
# This script fetches the current open tabs in all Safari windows.  
# Useful to run remotely on your mac when you are at work and want 
# to read a page you have open (remotely) at home but don't remember 
# the url but can log in to your home system on the cmmand line
#

from datetime import datetime
import logging
import sys
import time

# work around needed for if not using the system python (such as with anaconda python distrib)
#mod_path = '/System/Library/Frameworks/Python.framework/Versions/{0:}.{1:}/Extras/lib/python/PyObjC'.format( sys.version_info[0], sys.version_info[1] )
#sys.path.append(mod_path)

from Foundation import NSAppleScript
from AppKit import NSWorkspace

from ConfigsManager import ConfigsManager
import Constants
from DateMonitoring import DateMonitoring
from StorageManager import StorageManager
from TelegramBot import TelegramBot

log = logging.getLogger("APP." + __name__)
SAFARI = "Safari"
CHROME = "Google Chrome"

class BrowserTab:
    index: int
    url: str
    name: str
    def __init__(self, index: int, url: str, name: str):
        self.index = index
        self.url = url
        self.name = name


class BrowserWindow:
    window_id: int
    browser_name: str
    tabs: list[BrowserTab]
    def __init__(self, window_id: int, browser_name: str = SAFARI):
        self.window_id = window_id
        self.browser_name = browser_name
        self.tabs = []
    
    def add_tab(self, tab: BrowserTab):
        self.tabs.append(tab)

class Monitoring:

    __storage_manager : StorageManager
    __date_monitoring : DateMonitoring = None
    __prev_focused_app = ""
    __prev_successful_exec_timestamp : float = 0

    # Number of times a page/application were closed. If closed more than 3 time a special message will be sent to the user
    __logging_closed : dict[str, int] = {}

    def __init__(self):
        self.__storage_manager = StorageManager()
        self.setup_date_monitor()

    def setup_date_monitor(self):
        today = datetime.today().strftime('%Y-%m-%d')
        if self.__date_monitoring and self.__date_monitoring.date == today:
            return
        self.__logging_closed = {}
        monitorings = self.__storage_manager.retrieve_day_monitoring(today)
        if not monitorings:
            self.__storage_manager.add_day_monitoring(DateMonitoring(today, {})) 
            if self.__date_monitoring:
                log.info(f"Day report: {str(self.__date_monitoring)}")
                TelegramBot.send_message(f"Day report: {str(self.__date_monitoring)}")
            self.__date_monitoring = DateMonitoring(today, {})
        else:
            self.__date_monitoring = monitorings[0]

    def should_discard_this_execution(self):
        if abs(time.time() - self.__prev_successful_exec_timestamp - Constants.TICKER_TIME) > 2:
            log.info("Discard execution as most likely we skipped some tracking or we've just launched this tool")
            return True
        else:
            return False
        
    def monitor_application(self, configs: ConfigsManager):
        now_hour_minute = datetime.today().strftime('%H:%M')
        focused_application = self.get_front_most_application()
        application_name = focused_application["NSApplicationName"]
        app_cfg = configs.get_application_cfg(application_name)
        if app_cfg:
            if configs.is_full_blackout():
                log.info("We are in blackout mode. Killing without checking the limit")
                self.quit_application(application_name, configs, "blackout mode")
            if application_name not in self.__date_monitoring.data:
                self.__date_monitoring.data[application_name] = 0
            if configs.is_within_time_limit(app_cfg, now_hour_minute):
                log.debug(f"Increase counter for application {application_name}")
                if self.__prev_focused_app == application_name:
                    self.__date_monitoring.data[application_name] += Constants.TICKER_TIME
                else:
                    self.__date_monitoring.data[application_name] += (Constants.TICKER_TIME / 2)
                if configs.limit_reached(app_cfg, application_name, self.__date_monitoring.data[application_name]):
                    log.info(f"Quit app {application_name} because limit is reached")
                    self.quit_application(application_name, configs, "limit is reached")
                self.__storage_manager.update_day_monitoring(self.__date_monitoring)
            else:
                log.info(f"Quit app {application_name} because not inside defined time interval")
                self.quit_application(application_name, configs, "not in interval")
        self.__prev_focused_app = application_name

    def monitor_urls(self, configs: ConfigsManager, all_windows: list[BrowserWindow]):
        log.debug("monitor urls")
        now_hour_minute = datetime.today().strftime('%H:%M')
        for window in all_windows:
            log.debug(f"window {len(window.tabs)} {id(window)} {window.window_id}")
            for tab in window.tabs:
                if configs.is_in_whitelisted_urls(tab.url) or configs.is_in_whitelisted_names(tab.name):
                    continue
                url_cfg_obj = configs.get_blacklisted_url(tab.url)
                if url_cfg_obj:
                    url_cfg_str = url_cfg_obj["url"]
                    if configs.is_full_blackout():
                        log.info("We are in blackout mode. Killing without checking the limit")
                        self.close_tab_with_name(window.window_id, tab, configs, "blackout mode", url_cfg_str, window.browser_name)
                    if url_cfg_str not in self.__date_monitoring.data:
                        self.__date_monitoring.data[url_cfg_str] = 0
                    if configs.is_within_time_limit(url_cfg_obj, now_hour_minute):
                        self.__date_monitoring.data[url_cfg_str] += Constants.TICKER_TIME
                        if configs.limit_reached(url_cfg_obj, url_cfg_str, self.__date_monitoring.data[url_cfg_str]):
                            log.info("Close tab because limit is reached")
                            self.close_tab_with_name(window.window_id, tab, configs, "limit is reached", url_cfg_str, window.browser_name)
                        self.__storage_manager.update_day_monitoring(self.__date_monitoring)
                    else:
                        log.info("Close tab because not inside defined time interval")
                        self.close_tab_with_name(window.window_id, tab, configs, "not in interval", url_cfg_str, window.browser_name)


    def monitor(self, configs_file: str):
        if not self.should_discard_this_execution():
            self.setup_date_monitor()

            configs = ConfigsManager(configs_file)

            #1. check applications. If application is in the list we need to update timer. If timer limit is reached close app
            self.monitor_application(configs)
            all_windows = self.get_all_windows(SAFARI) + self.get_all_windows(CHROME)
            #2. check whitelisted urls and blacklisted urls. 
            #   check urls. If blacklist (full domain or not)then 
            #   3.1 check if limit reached -> then close
            #   3.2 check if current time in the interval and if previous run contained the same blacklist match -> then increase timer by TIMERTICKER 
            #       3.2.1 if previous call there is no blacklist match increase by half of TIMERTICKER
            self.monitor_urls(configs, all_windows)
            self.__prev_all_windows = all_windows
        self.__prev_successful_exec_timestamp = time.time()

    def get_all_windows(self, browser_name : str = SAFARI) -> list[BrowserWindow]:
        # create applescript code object
        s = NSAppleScript.alloc().initWithSource_(
            'tell app "'+ browser_name + '" to {URL,name} of tabs of windows'
        )

        # execute AS obj, get return value
        result,_ = s.executeAndReturnError_(None)

        # since we said {URL,name} we should have two items
        assert result.numberOfItems() == 2 

        # find number of tabs based on number of groups in the URL set
        num_windows = result.descriptorAtIndex_(1).numberOfItems()

        # create a simple dictionary
        tabs = dict(( 'window {0:}'.format(win_num), []) for win_num in range(1, num_windows+1) )
        list_of_windows = []
        for page_idx in range(1, num_windows+1):
            window = BrowserWindow(int(page_idx), browser_name)
            for tab_num in range(1, result.descriptorAtIndex_(1).descriptorAtIndex_(page_idx).numberOfItems()+1 ):
                tab = BrowserTab(tab_num,
                                 result.descriptorAtIndex_(1).descriptorAtIndex_(page_idx).descriptorAtIndex_(tab_num).stringValue(),
                                 result.descriptorAtIndex_(2).descriptorAtIndex_(page_idx).descriptorAtIndex_(tab_num).stringValue())
                window.add_tab(tab)
            list_of_windows.append(window)
        return list_of_windows
        

    def close_tab_with_name(self, window_id, tab : BrowserTab, configs: ConfigsManager, reason: str, matched_regex: str, browser_name : str = SAFARI):
        if configs.is_full_release():
            return
        TelegramBot.send_message(f"Closing tab with name {tab.name} as {reason}")
        if browser_name == SAFARI:
            s = NSAppleScript.alloc().initWithSource_(
                f'''
                tell application "{SAFARI}"
                    close (every tab of window {window_id} whose index is equal to {tab.index})
                end tell'''
            )
            result,_ = s.executeAndReturnError_(None)
        else:
            s = NSAppleScript.alloc().initWithSource_(
                f'''
                tell application "{CHROME}"
                    repeat with win in windows
                        close (tabs of win whose title is "{tab.name}")
                    end repeat
                end tell'''
            )
            result,_ = s.executeAndReturnError_(None)
        self.post_process(matched_regex)

    def get_front_most_application(self):
        last_active_name = ""
        active_app = NSWorkspace.sharedWorkspace().activeApplication()
        return active_app

    def quit_application(self, application_name: str, configs: ConfigsManager, reason: str):
        if configs.is_full_release():
            return
        TelegramBot.send_message(f"Quitting application : {application_name} as {reason}")
        s = NSAppleScript.alloc().initWithSource_(
            f'''tell application "{application_name}"
                    quit
                end tell'''
        )
        result,_ = s.executeAndReturnError_(None)
        self.post_process(application_name)

    def post_process(self, name):
        if name in self.__logging_closed:
            self.__logging_closed[name] += 1
        else:
            self.__logging_closed[name] = 1
        if self.__logging_closed[name] > 2:
            TelegramBot.send_message(f"Go back to work!")


            
        
        
                