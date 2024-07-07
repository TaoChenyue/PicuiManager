import logging.handlers
from pathlib import Path


def get_logger(log_file: str) -> logging.Logger:
    log_file: Path = Path(log_file)
    Path(log_file).parent.mkdir(exist_ok=True, parents=True)
    logger = logging.getLogger(log_file.name)
    logger.setLevel(logging.DEBUG)
    streamhandler = logging.StreamHandler()
    filehandler = logging.handlers.TimedRotatingFileHandler(
        log_file.as_posix(),
        when="D",
        interval=1,
        backupCount=7,
        encoding="utf-8",
    )
    logger.addHandler(filehandler)
    logger.addHandler(streamhandler)
    return logger
