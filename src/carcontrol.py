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


# Uncomment and change port to attach drive motor 1
@attach(CPlusXLMotor,
        name='drive_motor1',
        port=0,
        capabilities=[('sense_speed', 5)])
# Uncomment and change port to attach drive motor 2
@attach(CPlusXLMotor,
        name='drive_motor2',
        port=1,
        capabilities=[('sense_speed', 5)])
# Uncomment and change port to attach drive motor 3
# @attach(CPlusXLMotor,
#         name='drive_motor3',
#         port=0,
#         capabilities=[('sense_speed', 5), 'sense_pos'])
# Uncomment and change port to attach drive motor 4
# @attach(CPlusXLMotor,
#         name='drive_motor4',
#         port=0,
#         capabilities=[('sense_speed', 5), 'sense_pos'])
# Uncomment and change port to attach steering motor
@attach(CPlusLargeMotor,
        name='steering_motor',
        port=2,
        capabilities=['sense_pos'])
# Uncomment and change port to attach left indicators
@attach(Light,
        name='left_indicators',
        port=3)
# Uncomment and change port to attach right indicators
# @attach(Light,
#         name='right_indicators',
#         port=0)
# Uncomment and change port to reverse lights
# @attach(Light,
#         name='reverse_lights',
#         port=0)
# Uncomment and change port to brake lights
# @attach(Light,
#         name='brake_lights',
#         port=0)
# Uncomment and change port to tail lights
# @attach(Light,
#         name='tail_lights',
#         port=0)
# Uncomment and change port to high beams
# @attach(Light,
#         name='high_beams',
#         port=0)
# Uncomment and change port to attach headlights
# @attach(Light,
#         name='headlights',
#         port=0)
class Car(CPlusHub):

    def __init__(self,
                 name: str,
                 query_port_info: bool = False,
                 ble_id: str = None):
        super().__init__(name, query_port_info, ble_id)

        # Init status variables
        self._speed = 0
        self._steering_pos = 0
        self._steering_max_left = None
        self._steering_max_right = None
        self._headlight_status = False
        self._tail_light_status = False
        self._high_beam_status = False
        self._brake_light_status = False
        self._reverse_light_status = False
        self._left_indicator_status = False
        self._right_indicator_status = False

    async def set_speed(self, body: dict):
        """
        Set car speed.

        :param body: Target "speed" command body.

        """
        # Motor/car speed 0-100
        self._speed = body['speed']

        # Set requested speed in motor(s)
        await self.drive_motor1.set_speed(self._speed)
        await self.drive_motor2.set_speed(self._speed)
        await sleep(2)
    # TODO work in progress
    async def set_steering_position(self, body: dict):
        """
        Set car steering position.

        :param body: Target "steering" command body.

        """
        # Set steering position in degrees
        # -90 = full left
        # 90 = full right
        self._steering_pos = body['position']

        # Steering speed
        speed = 10
        if 'speed' in body:
            speed = body['speed']

        # Max percentage power that will be applied for steering (0-100%)
        max_power = 20
        if 'max_power' in body:
            max_power = body['max_power']

        # Set requested position in steering motor
        await self.steering_motor.set_pos(pos=self._steering_pos,
                                          speed=speed,
                                          max_power=max_power)
        await sleep(2)

    async def set_headlight_brightness(self, body: dict):
        """
        Set headlamp brightness.

        :param body: Target "headlights" command body.

        """
        # Light brightness 0-100
        brightness = body['brightness']

        # Light will be on for this long in seconds
        duration = 0
        if 'duration' in body:
            duration = body['duration']

        # Set status
        if brightness == 0:
            self._headlight_status = False
        else:
            self._headlight_status = True

        # Set requested brightness in light(s)
        await self.headlights.set_brightness(brightness)
        if duration > 0:
            await sleep(duration)
            await self.headlights.set_brightness(0)
        await sleep(1)

    async def set_high_beam_brightness(self, body: dict):
        """
        Set high beam brightness.

        :param body: Target "high_beams" command body.

        """
        # Light brightness 0-100
        brightness = body['brightness']

        # Light will be on for this long in seconds
        duration = 0
        if 'duration' in body:
            duration = body['duration']

        # Set status
        if brightness == 0:
            self._high_beam_status = False
        else:
            self._high_beam_status = True

        # Set requested brightness in light(s)
        await self.high_beams.set_brightness(brightness)
        if duration > 0:
            await sleep(duration)
            await self.high_beams.set_brightness(0)
        await sleep(1)

    async def set_tail_light_brightness(self, body: dict):
        """
        Set tail light brightness.

        :param body: Target "tail_lights" command body.

        """
        # Light brightness 0-100
        brightness = body['brightness']

        # Light will be on for this long in seconds
        duration = 0
        if 'duration' in body:
            duration = body['duration']

        # Set status
        if brightness == 0:
            self._tail_light_status = False
        else:
            self._tail_light_status = True

        # Set requested brightness in light(s)
        await self.tail_lights.set_brightness(brightness)
        if duration > 0:
            await sleep(duration)
            await self.tail_lights.set_brightness(0)
        await sleep(1)

    async def set_brake_light_brightness(self, body: dict):
        """
        Set brake light brightness.

        :param body: Target "brake_lights" command body.

        """
        # Light brightness 0-100
        brightness = body['brightness']

        # Light will be on for this long in seconds
        duration = 0
        if 'duration' in body:
            duration = body['duration']

        # Set status
        if brightness == 0:
            self._brake_light_status = False
        else:
            self._brake_light_status = True

        # Set requested brightness in light(s)
        await self.brake_lights.set_brightness(brightness)
        if duration > 0:
            await sleep(duration)
            await self.brake_lights.set_brightness(0)
        await sleep(1)

    async def set_reverse_light_brightness(self, body: dict):
        """
        Set reverse light brightness.

        :param body: Target "reverse_lights" command body.

        """
        # Light brightness 0-100
        brightness = body['brightness']

        # Light will be on for this long in seconds
        duration = 0
        if 'duration' in body:
            duration = body['duration']

        # Set status
        if brightness == 0:
            self._reverse_light_status = False
        else:
            self._reverse_light_status = True

        # Set requested brightness in light(s)
        await self.reverse_lights.set_brightness(brightness)
        if duration > 0:
            await sleep(duration)
            await self.reverse_lights.set_brightness(0)
        await sleep(1)

    async def set_indicator_lights(self, body: dict):
        """
        Set indicator light operation.

        :param body: Target "indicator_lights" command body.

        """
        # Light brightness 0-100
        brightness = body['brightness']

        # Indicators will be operating this long (seconds)
        duration = 0
        if 'duration' in body:
            duration = body['duration']

        # How long indicators will on each time (seconds)
        length = 0.5
        if 'length' in body:
            length = body['length']

        # Time between indicators lights on (seconds)
        interval = 0.75
        if 'interval' in body:
            interval = body['interval']

        # If left indicator should be operating
        left = False
        if 'left' in body:
            left = body['left']

        # If right indicator should be operating
        right = False
        if 'right' in body:
            right = body['right']

        # Set indicator status on
        if left:
            self._left_indicator_status = True
        if right:
            self._right_indicator_status = True

        # Set requested indicator operation
        current_duration = 0.0
        while duration == 0 or current_duration <= duration:
            # Turn on requested indicator lights
            if left:
                await self.left_indicators.set_brightness(brightness)
            if right:
                await self.right_indicators.led1.set_brightness(brightness)
            # Wait while indicator lights are on
            await sleep(length)
            # Turn off requested indicator lights
            if left:
                await self.left_indicators.set_brightness(0)
            if right:
                await self.right_indicators.set_brightness(0)
            # Wait while indicator lights are off
            await sleep(interval - length)
            # Go to next interval
            current_duration += interval
        await sleep(1)

        # Set indicator status off
        if left:
            self._left_indicator_status = False
        if right:
            self._right_indicator_status = False

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
                print(body)  # TODO delete when logging implemented
                if body['command'] == 'speed':
                    await self.set_speed(body=body)
                elif body['command'] == 'steering':
                    await self.set_speed(body=body)
                elif body['command'] == 'headlights':
                    await self.set_headlight_brightness(body=body)
                elif body['command'] == 'high_beams':
                    await self.set_high_beam_brightness(body=body)
                elif body['command'] == 'tail_lights':
                    await self.set_tail_light_brightness(body=body)
                elif body['command'] == 'brake_lights':
                    await self.set_brake_light_brightness(body=body)
                elif body['command'] == 'reverse_lights':
                    await self.set_reverse_light_brightness(body=body)
                elif body['command'] == 'indicators':
                    await self.set_indicator_lights(body=body)
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
        self._speed = self.drive_motor1.speed

    async def drive_motor2_change(self):
        self._speed = self.drive_motor2.speed

    async def steering_motor_change(self):
        self.message_info(
            f'Train sensor value change {self.train_sensor.value}')
        distance = self.train_sensor.value[
            VisionSensor.capability.sense_distance]
        count = self.train_sensor.value[VisionSensor.capability.sense_count]


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
