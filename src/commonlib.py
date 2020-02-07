# -*- coding: utf-8 -*-

"""
.. moduleauthor:: John Brännström <john.brannstrom@gmail.com>

Common library
**************

This module contains functions and classes used by multiple legcocar modules.

"""

# Built in modules
import logging
from logging import Logger
from logging import CRITICAL, ERROR, WARNING, DEBUG, INFO

# Third party modules
import coloredlogs
import verboselogs
from verboselogs import SUCCESS, NOTICE, SPAM, VERBOSE


def create_logger(log_file: str = None,
                  screen: bool = False,
                  level: str = logging.INFO):
    """
    Create a logging object.

    :param log_file: Full path and name of log file.
    :param screen:   If logging should also be done to screen.
    :param level:    Logging verbosity level.
    :rtype:          logging.Logger
    :return:         A logger object.

    """
    # Create logger
    logger_name = 'screen'
    if log_file is not None:
        logger_name = log_file.split('/')[-1]
    logger = verboselogs.VerboseLogger(name=logger_name)
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
            'critical': {'color': 'red', 'bold': True},
            'error': {'color': 'white',
                      'background': 'red', 'bold': True},
            'success': {'color': 'green', 'bold': True},
            'warning': {'color': 'yellow'},
            'notice': {'color': 'magenta'},
            'info': {},
            'verbose': {'color': 'blue'},
            'debug': {'color': 'green'},
            'spam': {'color': 'green', 'faint': True}
         }
        coloredlogs.install(logger=logger)

    # Add logging to file
    if log_file is not None:
        file_handler = logging.FileHandler(filename=log_file,
                                           encoding='utf-8')
        formatter = logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s')
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    # Return the logger
    return logger
