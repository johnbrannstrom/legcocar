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
        name='drive_motor1',
        port=0,
        capabilities=[('sense_speed', 5), 'sense_pos'])
@attach(CPlusXLMotor,
        name='drive_motor2',
        port=1,
        capabilities=[('sense_speed', 5), 'sense_pos'])
@attach(CPlusLargeMotor,
        name='steering_motor',
        port=2,
        capabilities=[('sense_speed', 5), 'sense_pos'])
@attach(Light,
        name='led1',
        port=3)
# @attach(CPlusXLMotor, name='rear_drive', port=1)
class Car(CPlusHub):

    def __init__(self):
        """
        Initializes car.

        """
        self._speed = 0

    async def set_speed(self, body: dict):
        """
        Set car speed.

        :param body: Target "speed" command body.

        """
        # Motor/car speed 0-100
        speed = body['speed']

        # Set requested speed in motor(s)
        await self.drive_motor1.set_speed(speed)
        await self.drive_motor2.set_speed(speed)
        await sleep(2)

    async def set_headlamp_brightness(self, body: dict):
        """
        Set headlamp brightness.

        :param body: Target "headlamps" command body.

        """
        # Light brightness 0-100
        brightness = body['brightness']

        # Light will be on for this long in seconds
        duration = body['duration']

        # Set requested brightness in light(s)

        evt = curio.Event()
        # Create a few waiters
        await curio.spawn(waiter(evt))

        await self.led1.set_brightness(brightness)
        await sleep(duration) # TODO this does not work its paralell
        await self.led1.set_brightness(0)

    async def set_high_beam_brightness(self, body: dict):
        """
        Set high beam brightness.

        :param body: Target "high_beam" command body.

        """
        # Light brightness 0-100
        brightness = body['brightness']

        # Set requested brightness in light(s)
        await self.led1.set_brightness(brightness)
        await sleep(1)

    async def set_rear_light_brightness(self, body: dict):
        """
        Set rear light brightness.

        :param body: Target "rear_light" command body.

        """
        # Light brightness 0-100
        brightness = body['brightness']

        # Set requested brightness in light(s)
        await self.led1.set_brightness(brightness)
        await sleep(1)

    async def set_brake_light_brightness(self, body: dict):
        """
        Set brake light brightness.

        :param body: Target "brake_light" command body.

        """
        # Light brightness 0-100
        brightness = body['brightness']

        # Set requested brightness in light(s)
        await self.led1.set_brightness(brightness)
        await sleep(1)

    async def set_indicator_lights(self, body: dict):
        """
        Set indicator light operation.

        :param body: Target "indicator_lights" command body.

        """
        # Light brightness 0-100
        brightness = body['brightness']
        # TODO, Duration, length, intervall, left, right

        # Set requested brightness in light(s)
        await self.led1.set_brightness(brightness)
        await sleep(1)

    async def run(self):
        """
        Start car operation.

        """
        self.message_info("Running")

        while True:
            self.message_info("looping")
            method_frame, header_frame, body = (
                channel.basic_get(queue='to_lego'))
            if method_frame is not None:
                channel.basic_ack(method_frame.delivery_tag)
                body = json.loads(codecs.decode(body, 'utf-8'))
                print(body)
                if body['command'] == 'speed':
                    await self.set_speed(body)
                    await self.drive_motor1.set_speed(body['speed'])
                    await self.drive_motor2.set_speed(body['speed'])
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

    async def drive_motor1_change(self):
        pass

    async def drive_motor2_change(self):
        pass

    async def steering_motor_change(self):
        pass


async def system():
    # hub = Car(name='hub1',
    #             query_port_info=True,
    #             ble_id="90:84:2B:4D:03:F7")
    hub = Car(name='hub2',
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
