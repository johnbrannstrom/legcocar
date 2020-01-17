# -*- coding: utf-8 -*-
"""
.. moduleauthor:: John Brännström <john.brannstrom@gmail.com>

Settings
********

This module contains settings.

"""

import yaml
import os
import re
from shutil import copyfile


class Settings:
    """Settings container."""

    __CONFIG_PATH = '/etc/'
    """(*str*) Config file path."""

    __CONFIG_FILE_NAME = 'legcocar.conf'
    """(*str*) Config file name."""

    __TEMPLATE_CONFIG_FILE_NAME = 'legcocar_template.conf'
    """(*str*) Template config file name."""

    __PATH_WITH_SLASH_PARAMETERS = []
    """(*list*) Parameters in this list with always end with a slash."""

    __PATH_WITHOUT_SLASH_PARAMETERS = []
    """(*list*) Parameters in this list will never end with a slash."""

    __CONFIG_FILE = None
    """(*str*) Full path and name of config file."""

    __PROGRAM_PATH = None
    """(*str*) Path of the program."""

    @staticmethod
    def static_init():
        """
        Initialize settings.

        """
        # Init program path
        Settings.PROGRAM_PATH = program_path = (
            os.path.dirname(os.path.abspath(__file__)) + '/')
        # Init settings path
        if Settings.__CONFIG_PATH is None:
            Settings.__CONFIG_PATH = Settings.PROGRAM_PATH
        else:
            Settings.__CONFIG_PATH = Settings._format_path(
                Settings.__CONFIG_PATH, True)
        # Init config file from template if it doesn't exist
        Settings.__CONFIG_FILE = (
            Settings.__CONFIG_PATH + Settings.__CONFIG_FILE_NAME)
        if not os.path.isfile(Settings.__CONFIG_FILE):
            template_config_file = (
                Settings.PROGRAM_PATH + Settings.__TEMPLATE_CONFIG_FILE_NAME)
            copyfile(template_config_file, Settings.__CONFIG_FILE)

    @staticmethod
    def load_settings_from_yaml():
        """
        Set system constants from YAML file.

        """
        with open(Settings.__CONFIG_FILE, 'r') as f:
            constants = yaml.load(f, Loader=yaml.FullLoader)
        for constant, value in constants.items():
            setattr(
                Settings, constant, Settings._format_value(constant, value))

    @staticmethod
    def write_settings_to_file(settings_json):
        """
        Write settings to file.

        :param dict settings_json: Settings that should be written to file.

        ..note:

            Comments are only supported on top level parameters.

        """
        file_obj = open(Settings.__CONFIG_FILE, 'r', encoding="utf-8")
        # Read YAML file comments from disk.
        lines = file_obj.readlines()
        file_obj.close()
        # Get all comments
        comment = []
        param_comments = {}
        for i in range(len(lines)):
            if len(lines[i]) > 0 and lines[i][0] == '#':
                comment.append(lines[i].strip())
                if lines[i+1][0] != '#':
                    param = re.match('(.+?):.*', lines[i+1]).group(1)
                    param_comments[param] = comment
                    comment = []
        # Set correct type of parameters
        for param, value in settings_json.items():
            settings_json[param] = Settings._format_value(param, value)
        # Create YAML with comments
        settings_yaml = yaml.dump(settings_json,
                                  default_flow_style=False,
                                  indent=4)
        settings_list = settings_yaml.split('\n')
        i = 0
        while i < len(settings_list):
            top_level_param = re.match('\A(\S+):.*\Z', settings_list[i])
            # Top level parameter found
            if top_level_param is not None:
                param = top_level_param.group(1)
                settings_list.insert(i, '')  # Add newline
                i += 1
                for test_param, comments in param_comments.items():
                    if param == test_param:
                        # Insert parameter comment
                        for comment in comments:
                            settings_list.insert(i, comment)
                            i += 1
                        del param_comments[param]
                        break
            i += 1
        settings_yaml = '\n'.join(settings_list)[1:]
        #  Write YAML to file
        with open(Settings.__CONFIG_FILE+'~', 'w') as file_obj:
            file_obj.writelines(settings_yaml)
        os.rename(Settings.__CONFIG_FILE+'~', Settings.__CONFIG_FILE)

    @staticmethod
    def _format_path(path, slash=True):
        """
        Format a path string.

        :param str path: Path to format.
        :param bool slash: If the path string should end with a slash
        :rtype: str
        :return: A formatted path string.

        """
        if len(path) == 0:
            return path
        elif slash and path[-1] != '/':
            return path + '/'
        elif not slash and path[-1] == '/':
            return path[:-1]
        return path

    @staticmethod
    def _format_value(param, value):
        """
        Format parameter value.

        :param str param: Name of the parameter to format.
        :param str param: Value to format.
        :rtype: str or bool
        :return: A parameter with the correct type.

        """
        if param in Settings.__PATH_WITH_SLASH_PARAMETERS:
            return Settings._format_path(value, True)
        elif param in Settings.__PATH_WITHOUT_SLASH_PARAMETERS:
            return Settings._format_path(value, False)
        elif str(value).lower() == 'yes' or str(value).lower() == 'true':
            return True
        elif str(value).lower() == 'no' or str(value).lower() == 'false':
            return False
        try:
            return int(value)
        except (TypeError, ValueError):
            return value
