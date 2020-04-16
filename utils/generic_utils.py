import logging
import time
from pathlib import Path


def project_root_path() -> Path:
    return Path(__file__).parent.parent


def set_up_logger(log_file_path : Path = None, logging_level: int = logging.INFO):
    logging.VERBOSE = 5
    logging.addLevelName(logging.VERBOSE, "VERBOSE")
    logging.Logger.verbose = lambda inst, msg, *args, **kwargs: inst.log(logging.VERBOSE, msg, *args, **kwargs)
    logging.verbose = lambda msg, *args, **kwargs: logging.log(logging.VERBOSE, msg, *args, **kwargs)

    if log_file_path:
        if not log_file_path.parent.exists():
            raise ValueError(f"Log file directory {log_file_path.parent} does not exist")
    logging.basicConfig(
        filename=log_file_path,
        level=logging_level,
        format='%(asctime)s %(name)-20s %(levelname)-10s %(message)s',
        datefmt="%Y-%m-%dT%H:%M:%S%z"
    )
    logging.Formatter.converter = time.gmtime
