# -*- coding: utf-8 -*-

"""
.. moduleauthor:: John Brännström <john.brannstrom@gmail.com>

Common library
**************

This module contains functions and classes used by multiple legcocar modules.

"""

# Built in modules
import logging

# Third party modules
import coloredlogs


def create_logger(log_file: str, level=logging.INFO, screen=False):
    """
    Create a logging object.

    :param log_file: Full path and name of log file.
    :param level:    Logging verbosity level.
    :param screen:   If logging should also be done to screen.
    :rtype:          logging.Logger
    :return:         A logger object.

    """
    # Create logger
    file_name = log_file.split('/')[-1]
    logger = logging.getLogger(name=file_name)
    logger.setLevel(level)

    # Add logging to screen
    if screen:
        stream_handler = logging.StreamHandler()
        formatter = logging.Formatter('%(levelname)s: %(message)s')
        stream_handler.setFormatter(formatter)
        logger.addHandler(stream_handler)

    # Set colored logging for logging to screen
    coloredlogs.DEFAULT_DATE_FORMAT = '%Y-%m-%d %H:%M:%S'
    coloredlogs.DEFAULT_LOG_FORMAT = '%(levelname)s %(message)s'
    coloredlogs.DEFAULT_FIELD_STYLES = {
        'asctime': {'color': None},
        'hostname': {'color': None},
        'levelname': {'color': 'black', 'bold': True},
        'name': {'color': None},
        'programname': {'color': None}
    }
    coloredlogs.DEFAULT_LEVEL_STYLES = {
        'critical': {'color': 'white', 'background': 'red', 'bold': True},
        'debug': {'color': 'green'},
        'error': {'color': 'red'}, 'info': {},
        'notice': {'color': 'magenta'},
        'spam': {'color': 'green', 'faint': True},
        'success': {'color': 'green', 'bold': True},
        'verbose': {'color': 'blue'},
        'warning': {'color': 'yellow'}
    }
    coloredlogs.install(logger=logger)

    # Add logging to file
    file_handler = logging.FileHandler(filename=log_file, encoding='utf-8')
    formatter = logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s')
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    # Return the logger
    return logger
