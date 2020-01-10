#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
.. moduleauthor:: John Brännström <john.brannstrom@gmail.com>

Car control
***********

This module controls a car vis the LEGO control+ Bluetooth interface.

"""

import logging
from curio import sleep
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


async def system():
    hub = Truck(name='hub1',
                query_port_info=True,
                ble_id="90:84:2B:4D:03:F7")
    # hub = Truck('hub1', True, ble_id="4A:42:1A:27:06:94")
    # hub = Truck('hub1', True, ble_id="50:D2:9D:10:B1:F6")
    # hub = Truck(name='hub1',
    #             query_port_info=True,
    #             ble_id="00001624-1212-efde-1623-785feabcd123")
    # hub = Truck('hub1', True)

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    start(system)
