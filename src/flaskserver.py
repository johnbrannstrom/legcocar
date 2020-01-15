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

# Third party modules
from flask import Flask, render_template, request, Response
import pika


# noinspection PyTypeChecker,PyBroadException
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


    def handle_request(self):
        """
        Handle a HTTP request.

        """
        args = self._get_request_arguments()
        path = request.path
        content_type = request.content_type
        try:
            if path.startswith('/api/'):
                # Connect to RabbitMQ if request is an API request
                connection = pika.BlockingConnection(
                    pika.ConnectionParameters('localhost'))
                channel = connection.channel()
                channel.queue_declare(queue='to_lego')
            if (path.startswith('/api/') and
                    not content_type.startswith('application/json')):
                raise HttpRequestContentTypeError(
                    path=path,
                    content_type=content_type,
                    wanted_type='application/json')
            # Handle requests
            if path == '/':
                response = render_template('index.html')
            elif path == '/api/run_motor' and request.method == 'POST':
                mandatory_args = {'hub': 'str', 'id': 'str', 'speed': 'int'}
                optional_args = {}
                self._validate_arguments(path=path,
                                         args=args,
                                         mandatory_args=mandatory_args,
                                         optional_args=optional_args)
                args['command'] = 'run_motor'
                body = json.dumps(args)
                # Send message to to RabbitMQ
                channel.basic_publish(exchange='',
                                      routing_key='to_lego',
                                      body=body)
                message = "Speed set to '{}'".format(args['speed'])
                response = self._json_response(message=message,
                                               status_code=200)
            # Close connection to RabbitMQ if request is an API request
            if path.startswith('/api/'):
                channel.close()
                connection.close()
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
        print(args) # TODO del
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
@web_server.route('/api/run_motor', methods=['POST'])
def index():
    """
    Handle incoming HTTP requests.

    """
    request_handler = RequestHandler()
    return request_handler.handle_request()


if __name__ == '__main__':
    main = Main()
    main.run()
