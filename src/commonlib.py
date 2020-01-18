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

    # Add logging to screen
    if screen:
        stream_handler = logging.StreamHandler()
        formatter = logging.Formatter('%(levelname)s:%(message)s')
        stream_handler.setFormatter(formatter)
        logger.addHandler(stream_handler)

    # Add logging to file
    file_handler = logging.FileHandler(filename=log_file, encoding='utf-8')
    formatter = logging.Formatter('%(asctime)s %(levelname)s:%(message)s')
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    # Return the logger
    return logger
