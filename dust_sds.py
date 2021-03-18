#!/usr/bin/env python
# -*- coding: utf-8 vi:noet
# Userspace driver for the Nova Fitness Co SDS (eg. SDS011) particulate matter sensor.
# SPDX-FileCopyrightText: 2020 Jérôme Carretero <cJ@zougloub.eu>
# SPDX-License-Identifier: MIT

"""
Refs:

- http://www.inovafitness.com/en/a/chanpinzhongxin/95.html

- https://www-sd-nf.oss-cn-beijing.aliyuncs.com/%E5%AE%98%E7%BD%91%E4%B8%8B%E8%BD%BD/SDS011%20laser%20PM2.5%20sensor%20specification-V1.4.pdf

- Protocol info, including commands (not supported):
  https://cdn.sparkfun.com/assets/parts/1/2/2/7/5/Laser_Dust_Sensor_Control_Protocol_V1.3.pdf

"""

import sys
import serial
import logging
import struct

logger = logging.getLogger(__name__)

class Dust_sds(object):
	def __init__(self, port="/dev/ttyUSB1"):
		self._port = port
		self._serial = None

	def __enter__(self):
		self._serial = ser = serial.Serial()
		ser.baudrate = 9600
		ser.port = self._port
		ser.timeout = 60
		ser.open()
		return self

	def __exit__(self, *args)
		self._serial.close()

	def read(self):
		ret = dict()

		while True:
			recvd = []
			data = self._serial.read(1)
			if data != b"\xAA":
				logger.werning("bad b0: %s", data)
				continue
			recvd.append(data)

			data = self._serial.read(1)
			if data != b"\xC0":
				logger.warning("bad b1: %s", data)
				continue

			recvd.append(data)

			pm25s = self._serial.read(2)
			recvd.append(pm25s)
			pm10s = self._serial.read(2)
			recvd.append(pm10s)

			zz = self._serial.read(2)
			recvd.append(zz)

			crc = self._serial.read(1)
			recvd.append(crc)

			data = self._serial.read(1)
			recvd.append(data)
			if data != b"\xAB":
				logger.warning("bad end marker: %s", data)
				continue

			recvd = b"".join(recvd)

			crc_mes = 0
			for x in recvd[2:8]:
				crc_mes = (crc_mes + x) & 0xff

			if crc_mes != crc[0]:
				logger.warning("bad crc: presented %s calculated %s",
				 crc[0], crc_mes)
				continue

			ret["PM2.5_ug_m3"] = struct.unpack("<h", pm25s)[0] / 10
			ret["PM10_ug_m3"] = struct.unpack("<h", pm10s)[0] / 10

			if self._serial.in_waiting == 0:
				return ret



if __name__ == '__main__':
	import datetime
	with Dust_sds() as s:
		while True:
			rec = s.read()
			now = datetime.datetime.now()
			sys.stdout.write("- time: %s\n" % (now.strftime("%Y-%m-%dT%H:%M:%S.%f")))
			for k, v in rec.items():
				sys.stdout.write("  %s: %s\n" % (k, v))
			sys.stdout.flush()
