#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
.. moduleauthor:: John Brännström <john.brannstrom@gmail.com>

Flask server
************

This modules is a flask web server.

"""

# Built in modules
import argparse

# Third party modules
import curio
from flask import Flask, render_template, request
from bricknil import attach, start
from bricknil.hub import CPlusHub
from bricknil.sensor.motor import CPlusXLMotor
from bricknil.sensor.motor import CPlusLargeMotor

class RequestHandler:
    """Flask web server."""

    @staticmethod
    def _get_request_arguments():
        """
        Parse request arguments

        :rtype:  json
        :return: Arguments.

        """
        args = {}
        if request.method == 'PUT' or request.method == 'POST':
            if len(request.form) > 0:
                for key in request.form.keys():
                    args[key] = request.form.get(key)
            else:
                args = request.get_json()
        else:
            for key in request.args.keys():
                args[key] = request.args.getlist(key)
        return args

    def handle_request(self):
        """
        Handle a HTTP request.

        """
        args = RequestHandler._get_request_arguments()
        if request.path == '':
            return render_template('index.html')
        # TODO delete, only for test
        elif request.path == '/api/test' and request.method == 'POST':
            return render_template('index.html')


class Main:
    """Contains the script"""

    @staticmethod
    def _parse_command_line_options():
        """
        Parse options from the command line.

        :rtype: Namespace

        """
        debug_help = 'Debugging printout level.'
        description = 'Start flask web server.'
        parser = argparse.ArgumentParser(description=description)
        parser.add_argument('--debug', type=int, default=0,
                            help=debug_help, required=False)
        args = parser.parse_args()
        return args

    def run(self):
        """
        Run the script.

        """
        args = self._parse_command_line_options()
        flask_debug = False
        if args.debug > 0:
            flask_debug = True
        web_server.run(debug=flask_debug,
                       threaded=False,
                       host='0.0.0.0',
                       port=80,
                       processes=8)


web_server = Flask(__name__,
                   static_url_path="",
                   static_folder='/srv/legcocar/html_static',
                   template_folder='/srv/legcocar/html_templates')
web_server.strict_slashes = False


@web_server.route('/', methods=['GET'])
@web_server.route('/index.html', methods=['GET'])
@web_server.route('/api/test', methods=['POST'])
def index():
    """
    Handle incoming HTTP requests.

    """
    request_handler = RequestHandler()
    return request_handler.handle_request()


if __name__ == '__main__':
    main = Main()
    main.run()
