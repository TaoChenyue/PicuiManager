import logging.handlers
from pathlib import Path


def get_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    streamhandler = logging.StreamHandler()
    logger.addHandler(streamhandler)
    return logger
