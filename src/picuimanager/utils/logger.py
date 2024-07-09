import logging.handlers
from pathlib import Path
from typing import Optional


def get_logger(log_file: Optional[str]) -> logging.Logger:
    logger = logging.getLogger("default" if log_file is None else log_file)
    logger.setLevel(logging.DEBUG)
    if not logger.hasHandlers():
        streamhandler = logging.StreamHandler()
        logger.addHandler(streamhandler)
    if log_file is None:
        return logger
    log_file: Path = Path(log_file)
    Path(log_file).parent.mkdir(exist_ok=True, parents=True)
    filehandler = logging.handlers.TimedRotatingFileHandler(
        log_file.as_posix(),
        when="D",
        interval=1,
        backupCount=7,
        encoding="utf-8",
    )
    logger.addHandler(filehandler)
    return logger
