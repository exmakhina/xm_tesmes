#!/usr/bin/env python
# -*- coding: utf-8 vi:noet
# Driver for USB Relay

"""

This is a userspace driver for the
Al (LC) LCUS - type 1 USB relay module USB intelligent switch control
module found at
http://www.lctech-inc.com/Hardware/Detail.aspx?id=d8e17734-4209-4e81-aace-aafc3c8ef764

"""

import time
import serial

code_open = bytes(bytearray([0xA0, 0x01, 0x01, 0xA2]))
code_close = bytes(bytearray([0xA0, 0x01, 0x00, 0xA1]))

class Relay_LCUS(object):
	def __init__(self, port="/dev/ttyUSB0"):
		ser = serial.Serial()
		ser.baudrate = 9600
		ser.port = port
		ser.timeout = 0.5
		ser.open()
		self._serial = ser

	def __del__(self):
		self._serial.close()

	def set(self, value):
		code = code_open if value else code_close
		data = self._serial.write(code)

if __name__ == '__main__':

	s = Relay_LCUS()
	for idx_loop in range(1):
		s.set(1)
		time.sleep(5)
		s.set(0)
	
