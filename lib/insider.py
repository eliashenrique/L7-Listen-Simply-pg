import logging
import logging.config
from datetime import date


def insid():
    date_object = date.today().strftime("%Y-%m-%d")
    logging.config.fileConfig(
        fname=f'logs/{date_object}.log',
        disable_existing_loggers=False
    )

    # Get the logger specified in the file
    logger = logging.getLogger(__name__)
    return logger
