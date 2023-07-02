import logging
import os
import json
import sqlite3
import time
from typing import List

from DateMonitoring import DateMonitoring

"""
    Storage is represented as a list of operations performed on Exchange 
    Every operation is freeform defined by each strategy
"""

log = logging.getLogger("APP." + __name__)
class StorageManager:
    PRD_STORAGE_NAME = "storage.db"
    TEST_STORAGE_NAME = "test_storage.db"
    # Strategy bom configs
    ID = "id"
    DATE = "date"
    DATA = "data"

    __db_connection: sqlite3.Connection

    def __init__(self, storage_name = "monitorings.db"):
        if not os.path.exists("storage"):
            os.makedirs("storage")
        self.__create_tables(storage_name)

    def __create_tables(self, storage_name):
        self.__db_connection = sqlite3.connect("storage/" + storage_name)

        cur = self.__db_connection.cursor()
        # Create table
        cur.execute(
            f"""CREATE TABLE if not exists day_monitoring ({self.DATE} text primary key, {self.DATA} text)"""
        )
        
        self.__db_connection.commit()        

    def add_day_monitoring(self, date_monitoring: DateMonitoring):
        # Insert a row of data
        cur = self.__db_connection.cursor()
        insert_request = f"""INSERT INTO day_monitoring({self.DATE}, {self.DATA}) VALUES (\'{date_monitoring.date}\', \'{date_monitoring.get_data_as_str()}\');"""
        log.debug(insert_request)
        cur.execute(insert_request)
        self.__db_connection.commit()

    def retrieve_day_monitoring(self, date: str) -> list[DateMonitoring]:
        cur = self.__db_connection.cursor()
        select_request = f"""SELECT {self.DATE}, {self.DATA} from day_monitoring WHERE {self.DATE}=\'{date}\';"""

        log.debug(select_request)
        results = list()
        for row in cur.execute(select_request):
            results.append(DateMonitoring(row[0], json.loads(row[1])))
        return results

    def update_day_monitoring(self, date_monitoring: DateMonitoring):
        cur = self.__db_connection.cursor()
        update_request = (
            f"""UPDATE day_monitoring set {self.DATA}=\'{date_monitoring.get_data_as_str()}\' WHERE {self.DATE}=\'{date_monitoring.date}\';"""
        )
        log.debug(update_request)
        cur.execute(update_request)
        self.__db_connection.commit()

    def retrieve_all_day_monitorings(self) -> list[DateMonitoring]:
        cur = self.__db_connection.cursor()
        select_request = f"""SELECT {self.DATE}, {self.DATA} from day_monitoring;"""

        log.debug(select_request)
        results = list()
        for row in cur.execute(select_request):
            results.append(DateMonitoring(row[0], json.loads(row[1])))
        return results