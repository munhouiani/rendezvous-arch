import logging
import sys

FORMATTER = logging.Formatter("%(asctime)s — %(name)s — %(levelname)s — %(message)s")

# one global console handler
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setFormatter(FORMATTER)

logger_dict = {}


def create_logger(logger_name):
    logger = logging.getLogger(logger_name)
    logger.addHandler(console_handler)
    logger.propagate = False

    return logger


def get_logger(logger_name, level=logging.DEBUG):
    if logger_name not in logger_dict:
        logger_dict[logger_name] = create_logger(logger_name)
    logger = logger_dict[logger_name]
    logger.setLevel(level)
    return logger
