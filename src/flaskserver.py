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
import json
import traceback
import re

# Third party modules
from flask import Flask, render_template, request, Response
import pika


# noinspection PyTypeChecker,PyBroadException
class RequestHandler:
    """Flask web server."""

    def __init__(self):
        # Init variables for connecting to RabbitMQ
        self._connection = None
        self._channel = None

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

    @staticmethod
    def _json_response(message, status_code, result=None):
        """
        Create a json HTTP response.
        :param str message:     Text message.
        :param int status_code: HTTP status code.
        :param json result:     If the response should contain information this
                                should be set.
        :rtype: Json
        :return: Json HTTP response
        """
        data = {
            'status': status_code,
            'message': message
        }
        if result is not None:
            data['result'] = result
        json_message = json.dumps(data)
        return Response(
            json_message, status=status_code, mimetype='application/json')

    # noinspection PySimplifyBooleanCheck
    @staticmethod
    def _validate_arguments(path: str, args: dict, mandatory_args: dict,
                            optional_args: dict):
        """
        Check that only valid arguments are passed to request.

        :param path:           HTTP request path.
        :param args:           HTTP request arguments.
        :param mandatory_args: Dictionary with the name and type of all
                               mandatory arguments.
        :param optional_args:  Dictionary with the name and type of all
                               mandatory arguments.
        :raises: HttpRequestError

        """
        all_args = {**mandatory_args, **optional_args}
        # Look for missing arguments
        missing_args = [i for i in mandatory_args.keys()
                        if i not in args.keys()]
        if missing_args != []:
            raise HttpRequestMissingArgumentError(
                args=missing_args, path=path)
        # Look for invalid arguments
        invalid_args = [
            i for i in args.keys() if i not in all_args.keys()]
        if invalid_args != []:
            raise HttpRequestInvalidArgumentError(
                args=invalid_args, path=path)
        # Look for arguments with wrong type
        for arg in args.keys():
            type_ = all_args[arg]
            value = args[arg]
            type_error = False
            # Verify string type parameters
            if type_ == 'str' and not type(value) == str:
                type_error = True
            # Verify int type parameters
            elif type_ == 'int' and not type(value) == int:
                type_error = True
            # Verify list type parameters
            elif type_ == 'list' and not type(value) == list:
                type_error = True
            # Verify bool type parameters
            elif type_ == 'bool' and not type(value) == bool:
                type_error = True
            # Verify dict type parameters
            elif type_ == 'dict' and not type(value) == dict:
                type_error = True
            elif type_ == 'float' and not type(value) == float:
                type_error = True
            # If we found a type error, raise it
            if type_error:
                raise HttpRequestArgumentTypeError(
                    path=path, arg=arg, arg_type=all_args[arg],
                    value=value)

    def _handle_api_request(self, mandatory_args: dict, optional_args: dict):
        """
        Handle a HTTP API request.

        :param mandatory_args: Dictionary describing mandatory arguments.
        :param optional_args:  Dictionary describing optional arguments.
        :rtype:   dict
        :returns: API response message.

        """
        # Get HTTP request arguments
        args = self._get_request_arguments()
        # Get HTTP request path
        path = request.path
        self._validate_arguments(path=path,
                                 args=args,
                                 mandatory_args=mandatory_args,
                                 optional_args=optional_args)
        # Get command from path
        args['command'] = re.match('.*/(.+)', string=path).group(1)
        # Set body
        body = json.dumps(args)
        # Send message to to RabbitMQ
        self._channel.basic_publish(exchange='',
                                    routing_key='to_lego',
                                    body=body)
        # message = 'Speed set to {}'.format(args['speed'])
        return self._json_response(message=str(args),
                                   status_code=200)

    def handle_request(self):
        """
        Handle a HTTP request.

        """
        path = request.path
        content_type = request.content_type
        try:
            if path.startswith('/api/'):
                # Connect to RabbitMQ if request is an API request
                self._connection = pika.BlockingConnection(
                    pika.ConnectionParameters('localhost'))
                self._channel = self._connection.channel()
                self._channel.queue_declare(queue='to_lego')
            if (path.startswith('/api/') and
                    not content_type.startswith('application/json')):
                raise HttpRequestContentTypeError(
                    path=path,
                    content_type=content_type,
                    wanted_type='application/json')

            # Handle requests
            response = None
            if path == '/':
                response = render_template('index.html')
            elif path == '/api/speed' and request.method == 'POST':
                mandatory_args = {'hub': 'str', 'speed': 'int'}
                optional_args = {}
                response = self._handle_api_request(
                    mandatory_args=mandatory_args,
                    optional_args=optional_args)
            elif path == '/api/headlights' and request.method == 'POST':
                mandatory_args = {'hub': 'str',
                                  'brightness': 'int'}
                optional_args = {'duration': 'int'}
                response = self._handle_api_request(
                    mandatory_args=mandatory_args,
                    optional_args=optional_args)
            elif path == '/api/indicators' and request.method == 'POST':
                mandatory_args = {'hub': 'str',
                                  'brightness': 'int'}
                optional_args = {'duration': 'int',
                                 'length': 'float',
                                 'interval': 'float',
                                 'left': 'bool',
                                 'right': 'bool'}
                response = self._handle_api_request(
                    mandatory_args=mandatory_args,
                    optional_args=optional_args)
            # Close connection to RabbitMQ if request was an API request
            if path.startswith('/api/'):
                self._channel.close()
                self._connection.close()
            return response
        except HttpRequestError as e:
            return self._json_response(message=str(e),
                                       status_code=400)
        except BaseException:
            traceback_message = traceback.format_exc()
            return self._json_response(message=traceback_message,
                                       status_code=500)


class HttpRequestError(Exception):
    """Error for malformed HTTP requests."""

    # noinspection PyUnresolvedReferences
    def __str__(self):
        """
        String representation function.

        """
        return self._message


# noinspection PyShadowingNames
class HttpRequestContentTypeError(HttpRequestError):
    """Error for malformed HTTP requests."""

    def __init__(self, path: str, content_type: str, wanted_type: str):
        """
        Constructor function.

        :param path: Target path that caused the error.
        :param content_type: Target content type that caused the error.
        :param wanted_type:  Wanted content type.

        """
        message = ("Invalid content type '{content_type}' in HTTP request "
                   "'{path}'. Wanted type is '{wanted_type}'")
        self._message = message.format(path=path,
                                       content_type=content_type,
                                       wanted_type=wanted_type)


class HttpRequestMissingArgumentError(HttpRequestError):
    """Error for malformed HTTP requests."""

    def __init__(self, path: str, args: list):
        """
        Constructor function.

        :param path: Target path that caused the error.
        :param args: List of missing arguments.

        """
        message = ("Missing arguments in HTTP request '{path}'. The following "
                   "arguments are missing: {args}")
        self._message = message.format(path=path, args=', '.join(args))


class HttpRequestInvalidArgumentError(HttpRequestError):
    """Error for malformed HTTP requests."""

    def __init__(self, path: str, args: list):
        """
        Constructor function.

        :param path: Target path that caused the error.
        :param args: List of invalid arguments.

        """
        message = ("Invalid arguments in HTTP request '{path}'. The following "
                   "arguments are invalid: {args}")
        self._message = message.format(path=path, args=', '.join(args))


class HttpRequestArgumentTypeError(HttpRequestError):
    """Error for malformed HTTP requests."""

    def __init__(self, path: str, arg: str, arg_type: str, value):
        """
        Constructor function.

        :param path:     Path when the error was risen.
        :param arg:      Argument that caused the error.
        :param arg_type: Target argument type.
        :param value:    Type that caused the error.

        """
        message = ("Invalid arguments in HTTP request '{path}'. Argument '{arg"
                   "}' has invalid {arg_type} value {value}")
        self._message = message.format(path=path, arg=arg, arg_type=arg_type,
                                       value=value)


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
@web_server.route('/api/speed', methods=['POST'])
@web_server.route('/api/headlights', methods=['POST'])
@web_server.route('/api/indicators', methods=['POST'])
def index():
    """
    Handle incoming HTTP requests.

    """
    request_handler = RequestHandler()
    return request_handler.handle_request()


if __name__ == '__main__':
    main = Main()
    main.run()
