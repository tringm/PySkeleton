from pathlib import Path
import logging


def project_root_path() -> Path:
    return Path(__file__).parent.parent


def set_up_logger(log_file_path : Path = None, default_logging_level=logging.INFO):
    if log_file_path:
        log_file_path = str(log_file_path)
    logging.basicConfig(filename=log_file_path, level=default_logging_level,
                        format='%(asctime)-5s %(name)-5s %(levelname)-10s %(message)s',
                        datefmt='%H:%M:%S')
    logging.VERBOSE = 5
    logging.addLevelName(logging.VERBOSE, "VERBOSE")
    logging.Logger.verbose = lambda inst, msg, *args, **kwargs: inst.log(logging.VERBOSE, msg, *args, **kwargs)
    logging.verbose = lambda msg, *args, **kwargs: logging.log(logging.VERBOSE, msg, *args, **kwargs)
