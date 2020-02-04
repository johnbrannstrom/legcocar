#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
.. moduleauthor:: John Brännström <john.brannstrom@gmail.com>

Car control
***********

This module controls a car vis the LEGO control+ Bluetooth interface.

"""

# Built in modules
import argparse
import logging
import codecs
import json
import traceback

# Third party modules
import pika
import curio
import txdbus
from curio import sleep
from bricknil import attach, start
from bricknil.hub import CPlusHub
from bricknil.sensor.motor import CPlusXLMotor, CPlusLargeMotor
from bricknil.sensor import Light

# Local modules
from settings import Settings
from commonlib import create_logger

# Status on connection to LEGO via Bluetooth
connected_to_Lego = False


@attach(CPlusXLMotor,
        name='drive1',
        port=0,
        capabilities=[('sense_speed', 5), 'sense_pos'])
@attach(CPlusXLMotor,
        name='drive2',
        port=1,
        capabilities=[('sense_speed', 5), 'sense_pos'])
@attach(CPlusLargeMotor,
        name='steering',
        port=2,
        capabilities=[('sense_speed', 5), 'sense_pos'])
@attach(Light,
        name='lights',
        port=3)
# @attach(CPlusXLMotor, name='rear_drive', port=1)
class Truck(CPlusHub):

    async def run(self):
        self.message_info("Running")

        # async def drive:
        #     pass

        while True:
            self.message_info("looping")
            method_frame, header_frame, body = (
                channel.basic_get(queue='to_lego'))
            if method_frame is not None:
                channel.basic_ack(method_frame.delivery_tag)
                body = json.loads(codecs.decode(body, 'utf-8'))
                print(body)
                if body['command'] == 'drive':
                    await self.drive1.set_speed(body['speed'])
                    await self.drive2.set_speed(body['speed'])
                elif body['command'] == 'lights':
                    await self.lights.set_brightness(body['on'])
                await sleep(2)
            await sleep(0.1)

        # await self.motor.ramp_speed(80, 5000)

        # TODO keep this as working examples
        # Turn motor
        # self.message_info('Turn motor')
        # await self.drive1.set_pos(90, speed=10)
        # await sleep(20)
        # await self.drive1.set_pos(180, speed=10)
        # await sleep(20)
        # await self.drive1.set_pos(270, speed=10)
        # await sleep(20)
        # await self.drive1.set_pos(360, speed=10)
        # await sleep(20)
        # Set motor speed
        # self.message_info('Set motor speed')
        # await self.drive1.set_speed(-100)
        # await sleep(20)
        # await self.drive1.set_speed(0)
        # Ramp motor speed
        # self.message_info('Ramp motor speed')
        # await self.drive1.ramp_speed(target_speed=100,
        #                              ramp_time_ms=5000)
        # await sleep(20)
        # await self.drive1.ramp_speed(target_speed=-100,
        #                              ramp_time_ms=5000)
        # await sleep(20)

    async def drive1_change(self):
        pass

    async def drive2_change(self):
        pass

    async def steering_change(self):
        pass

async def system():
    # hub = Truck(name='hub1',
    #             query_port_info=True,
    #             ble_id="90:84:2B:4D:03:F7")
    hub = Truck(name='hub2',
                query_port_info=True,
                ble_id='90:84:2B:4E:35:B4')


class Main:
    """Contains the script"""

    @staticmethod
    def _parse_command_line_options():
        """
        Parse options from the command line.

        :rtype: Namespace
        :returns: Command line arguments.

        """
        log_verbosity_help = 'Logging verbosity 0-60.'
        description = 'Connects a LEGO Control+ Bluetooth hub to RabbitMQ.'
        parser = argparse.ArgumentParser(description=description)
        parser.add_argument('--log-verbosity', '-v', type=int,
                            help=log_verbosity_help, required=False)
        args = parser.parse_args()
        return args

    def run(self):
        """
        Run the script.

        """
        # Read settings from YAML file
        Settings.static_init()
        Settings.load_settings_from_yaml()

        # Connect to log file
        message_log = create_logger(log_file=Settings.MESSAGE_LOG,
                                    level=logging.INFO, screen=False)
        error_log = create_logger(log_file=Settings.ERROR_LOG,
                                  level=60, screen=False)

        # Parse command line options
        args = self._parse_command_line_options()
        if args.log_verbosity is not None:
            Settings.LOG_VERBOSITY = args.log_verbosity

        # Connect to LEGO Control+ hub
        # try:
        while True:
            start(system)
            break
        # except BaseException:
        #     message = traceback_message = traceback.format_exc()


if __name__ == '__main__':

    # Connect to RabbitMQ
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(host='localhost'))
    channel = connection.channel()
    channel.queue_declare(queue='to_lego')

    main = Main()
    main.run()

    # Close connection to RabbitMQ
    channel.close()
    connection.close()
