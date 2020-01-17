# -*- coding: utf-8 -*-

"""
.. moduleauthor:: John Brännström <john.brannstrom@gmail.com>

Common library
**************

This module contains functions and classes used by multiple legcocar modules.

"""

import logging


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

    # Add log levels DEBUG1/51 to DEBUG10/60
    for i in range(1, 10):
        logging.addLevelName(i+50, 'DEBUG%i' % i)

    # Add logging to screen
    if screen:
        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter('%(levelname)s:%(message)s')

    # Add logging to file
    file_handler = logging.FileHandler(filename=log_file, encoding='utf-8')
    file_handler.setFormatter('%(asctime)s %(levelname)s:%(message)s')
    logger.addHandler(file_handler)

    # Return the logger
    return logger
