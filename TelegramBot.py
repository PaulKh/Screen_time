import json
import requests
import logging

log = logging.getLogger("APP." + __name__)

class TelegramBot():
    failed_messages = set()

    #"auth_configs.cfg" file is needed to enable telegram bot with your keys
    # {
    #     "telegram_key": "key",
    #     "telegram_user_id": user_id_int
    # }
    @staticmethod
    def send_message(message):
        with open("auth_configs.cfg") as json_file:
            configs = json.load(json_file)
            data = {
                'chat_id': configs["telegram_user_id"],
                'text': message
            }
            try:
                response = requests.post('https://api.telegram.org/bot' + configs["telegram_key"] + '/sendMessage', data=data)
                response_message = response.json()
                if response_message["ok"]:
                    return
                else:
                    log.error(response.text)
            except Exception as e:
                log.error("Failed to send message:" + message + str(e))
                TelegramBot.failed_messages.add("Failed to send telegram message")
            TelegramBot.failed_messages.add(message)


    