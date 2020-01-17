#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
.. moduleauthor:: John Brännström <john.brannstrom@gmail.com>

Car control
***********

This module controls a car vis the LEGO control+ Bluetooth interface.

"""

# Built in modules
import logging
import codecs
import json
import traceback

# Third party modules
import pika
import bleak
from curio import sleep
from bricknil import attach, start
from bricknil.hub import CPlusHub
from bricknil.sensor.motor import CPlusXLMotor

# Local modules
from settings import Settings
from logfile import LogFile

# Status on connection to LEGO via Bluetooth
connected_to_Lego = False

@attach(CPlusXLMotor,
        name='drive1',
        port=0,
        capabilities=[('sense_speed', 5), 'sense_pos'])
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
                await self.drive1.set_speed(body['speed'])
                await sleep(20)
                print(body)
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


# def get_one_rabbitmq_message():
#     while True:
#         method_frame, header_frame, body = channel.basic_get(queue='to_lego')
#         if method_frame is not None:
#             print(str(body))
#             return body
#         time.sleep(0.5)


async def system():
    hub = Truck(name='hub1',
                query_port_info=True,
                ble_id="90:84:2B:4D:03:F7")

if __name__ == '__main__':
    # Read settings from YAML file
    Settings.static_init()
    Settings.load_settings_from_yaml()

    # Connect to log file
    error_log = LogFile(file_name=Settings.ERROR_LOG,
                        verbosity=Settings.LOG_VERBOSITY)

    # Connect to RabbitMQ
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(host='localhost'))
    channel = connection.channel()
    channel.queue_declare(queue='to_lego')

    logging.basicConfig(level=logging.INFO)
    while not connected_to_Lego:
        try:
            start(system)
            connected_to_Lego = True
        except bleak.exc.BleakError as e:
            lines = [traceback.format_exc()]
            error_log.write(lines=lines, level=0, date_time=True)

    curio.errors.TaskError

    # Close connection to RabbitMQ
    channel.close()
    connection.close()
