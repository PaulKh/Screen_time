import json
import logging

log = logging.getLogger("APP." + __name__)

class DateMonitoring:
    data: dict
    date: str

    def __init__(self, date: str, data: dict):
        self.data = data
        self.date = date

    def get_data_as_str(self):
        return json.dumps(self.data)
    
    def __str__(self):
        result = f"Date: {self.date}\n"
        for key, val in self.data.items():
            result += f"{key} : {round(val)} secs"
        return result
