import logging
import os
import time
from logging.handlers import RotatingFileHandler


def setup_logger(log_file_name: str, level=logging.INFO, console_level=logging.INFO):
    logging.getLogger().setLevel(logging.WARNING)

    log_formatter = logging.Formatter(
        "%(asctime)s %(levelname)s %(name)s: %(funcName)s(%(lineno)d) %(message)s"
    )

    if not os.path.exists("logs"):
        os.makedirs("logs")
    log_file = f"logs/{log_file_name}"

    my_handler = RotatingFileHandler(
        log_file,
        mode="a",
        maxBytes=5 * 1024 * 1024,
        backupCount=2,
        encoding=None,
        delay=False
    )
    my_handler.setFormatter(log_formatter)
    my_handler.setLevel(level)

    ch = logging.StreamHandler()
    ch.setFormatter(log_formatter)
    ch.setLevel(console_level)

    logging.getLogger().setLevel(level)

    logging.getLogger().addHandler(my_handler)
    logging.getLogger().addHandler(ch)

    logging.getLogger("telegram.bot").setLevel(console_level)
    logging.getLogger("telegram.ext.updater").setLevel(console_level)
    logging.getLogger("apscheduler.scheduler").setLevel(console_level)