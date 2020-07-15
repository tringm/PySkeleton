import logging
import logging.config
import time
from functools import wraps
from pathlib import Path

DEFAULT_LOG_FORMAT = '%(asctime)s %(name)-20s %(levelname)-10s %(message)s'
DEFAULT_DATE_FORMAT = '%Y-%m-%dT%H:%M:%S%z'


def default_logging_config(
    logging_level: str = 'INFO',
    log_to_file: Path = None,
    file_logging_level: str = 'DEBUG'
):
    """logging config with 2 handlers of file and stdout
    """

    handlers_config = {
        'default': {
            'class': 'logging.StreamHandler',
            'formatter': 'default',
            'level': logging_level,
            'stream': 'ext://sys.stdout'
        }
    }
    if log_to_file:
        if not log_to_file.parent.exists():
            raise FileNotFoundError(f'{log_to_file.parent} not exist')
        handlers_config['file'] = {
            'class': 'logging.handlers.RotatingFileHandler',
            'formatter': 'default',
            'level': file_logging_level,
            'filename': str(log_to_file),
            'maxBytes': 10 * 1024 * 1024,
            'backupCount': 5
        }

    config_dict = {
        "version": 1,
        'disable_existing_loggers': False,
        "formatters": {
            'default': {
                'class': 'logging.Formatter',
                'format': DEFAULT_LOG_FORMAT,
                'datefmt': DEFAULT_DATE_FORMAT,
                'converter': 'time.gmtime'
            }
        },
        "handlers": handlers_config,
        'loggers': {
            '': {
                'handlers': list(handlers_config.keys()),
                'level': 'DEBUG'
            }
        }
    }
    logging.config.dictConfig(config_dict)


def log_exec_time(logger: logging.Logger, level: int = logging.DEBUG):
    def called(func):
        @wraps(func)
        def wrapped(*args, **kwargs):
            func_name = func.__name__
            logger.log(level=level, msg=f'{func_name} started')
            start = time.perf_counter()
            result = func(*args, **kwargs)
            logger.log(level=level, msg=f'{func_name} took {time.perf_counter() - start:.2f}s')
            return result
        return wrapped
    return called
