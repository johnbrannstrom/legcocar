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
from threading import Thread
import time

# Third party modules
import pika
from curio import sleep, UniversalQueue
from bricknil import attach, start
from bricknil.hub import CPlusHub
from bricknil.sensor.motor import CPlusXLMotor


@attach(CPlusXLMotor,
        name='motor1',
        port=0,
        capabilities=[('sense_speed', 5), 'sense_pos'])
# @attach(CPlusXLMotor, name='rear_drive', port=1)
class Truck(CPlusHub):

    async def run(self):
        self.message_info("Running")

        while True:
            self.message_info("looping")
            method_frame, header_frame, body = (
                channel.basic_get(queue='to_lego'))
            print(str(body))
            await sleep(0.1)

        # await self.motor.ramp_speed(80, 5000)

        # TODO keep this as working examples
        # Turn motor
        # self.message_info('Turn motor')
        # await self.motor1.set_pos(90, speed=10)
        # await sleep(20)
        # await self.motor1.set_pos(180, speed=10)
        # await sleep(20)
        # await self.motor1.set_pos(270, speed=10)
        # await sleep(20)
        # await self.motor1.set_pos(360, speed=10)
        # await sleep(20)
        # Set motor speed
        # self.message_info('Set motor speed')
        # await self.motor1.set_speed(-100)
        # await sleep(20)
        # await self.motor1.set_speed(0)
        # Ramp motor speed
        # self.message_info('Ramp motor speed')
        # await self.motor1.ramp_speed(target_speed=100,
        #                              ramp_time_ms=5000)
        # await sleep(20)
        # await self.motor1.ramp_speed(target_speed=-100,
        #                              ramp_time_ms=5000)
        # await sleep(20)

    async def motor1_change(self):
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
    # connect to
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(host='localhost'))
    channel = connection.channel()
    channel.queue_declare(queue='to_lego')

    logging.basicConfig(level=logging.INFO)
    start(system)

    channel.close()
    connection.close()
