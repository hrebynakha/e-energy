"""Custom formatter for logging"""

import logging


class CustomFormatter(logging.Formatter):
    """Custom formatter for logging"""

    grey = "\x1b[90m"
    green = "\x1b[92m"
    yellow = "\x1b[93m"
    red = "\x1b[91m"
    bold_red = "\x1b[31;1m"
    reset = "\x1b[0m"
    format_ = (
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s (%(filename)s:%(lineno)d)"
    )

    FORMATS = {
        logging.DEBUG: grey + format_ + reset,
        logging.INFO: green + format_ + reset,
        logging.WARNING: yellow + format_ + reset,
        logging.ERROR: red + format_ + reset,
        logging.CRITICAL: bold_red + format_ + reset,
    }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)


class CustomFileFormatter(logging.Formatter):
    """Custom formatter for logging"""

    format_ = (
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s (%(filename)s:%(lineno)d)"
    )

    def format(self, record):
        log_fmt = self.format_
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)


logger = logging.getLogger("bot")
logger.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
ch.setFormatter(CustomFormatter())
logger.addHandler(ch)
fh = logging.FileHandler("energybot.log")
fh.setLevel(logging.DEBUG)
fh.setFormatter(CustomFileFormatter())
logger.addHandler(fh)
