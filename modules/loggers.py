import logging
import logging.config

LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "simple": {"format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"}
    },
    "handlers": {
        "file": {
            "class": "logging.FileHandler",
            "level": "INFO",
            "formatter": "simple",
            "filename": "logs/system.log",
        }
    },
    "loggers": {"System": {"handlers": ["file"], "level": "INFO", "propagate": False}},
}
logging.config.dictConfig(LOGGING_CONFIG)
system_log = logging.getLogger("System")
