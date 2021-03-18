#!/usr/bin/env python
# -*- coding: utf-8 vi:noet
# “Driver” for Huanyang VFD on UART (RS-485)
# SPDX-FileCopyrightText: 2016-2021 Jérôme Carretero <cJ@zougloub.eu>
# SPDX-License-Identifier: MIT

"""

- Protocol information: https://www.exoror.com/datasheet/VFD.pdf

- Manufacturer information:

  https://www.nvcnc.net/huanyang-vfd.html
  https://www.nvcnc.net/pdf/HY-0.75kW~2.2kW-vfd.pdf
  https://www.nvcnc.net/pdf/Huanyang_English_Manual-c.pdf
  https://www.nvcnc.net/pdf/huanyang-vfd-manual.pdf
"""

import struct
import time
import logging
from enum import IntEnum

import serial

logger = logging.getLogger(__name__)

def crc_chk(buf) -> int:
	reg_crc = 0xffff

	for x in buf:
		reg_crc ^= x
		for j in range(8):
			if reg_crc & 0x01 != 0:
				reg_crc = (reg_crc>>1) ^ 0xa001
			else:
				reg_crc = reg_crc>>1

	v = reg_crc & 0xffff

	return [ v & 0xff, (v >> 8) & 0xff ]

	# != RTU: would be MSB first?
	#return [ (v >> 8) & 0xff, v & 0xff ]


class Function(IntEnum):
	FUNC_R = 0x01
	FUNC_W = 0x02
	CTRL_W = 0x03
	STAT_R = 0x04
	INV_FREQ_W = 0x05
	RESV_1 = 0x06
	RESV_2 = 0x07
	LOOP = 0x08

class ControlBit(IntEnum):
	RUN = 0
	FOR = 1
	REV = 2
	STOP = 3
	RF = 4
	JOG = 5
	JOGF = 6
	JOGR = 7

class Status(IntEnum):
	# Possibilities for Function.STAT_R
	SET_F = 0
	OUT_F = 1
	OUT_A = 2
	RoTT = 3
	DCV = 4
	ACV = 5
	CONT = 6
	TMP = 7

class VFD(object):
	def __init__(self, serial, addr=0x01):
		self._ser = serial
		self._addr = 0x01

	def call(self, func_code, request) -> bytes:
		addr = self._addr
		ser = self._ser

		req = request
		pkt = [
		 addr,
		 func_code,
		 len(req),
		] + req

		pkt += crc_chk(pkt)

		logger.debug("Sending %s", bytes(bytearray(pkt)).hex())

		ser.write(bytes(bytearray(pkt)))

		res_addr = ser.read(1)[0]
		if res_addr != addr:
			raise NotImplementedError(res_addr)

		func = ser.read(1)[0]
		if func != func_code:
			raise NotImplementedError(func)

		len_res = ser.read(1)[0]

		data = ser.read(len_res)

		crc = ser.read(2)

		if func_code == Function.STAT_R:
			what = data[0]
			if what != req[0]:
				raise NotImplementedError()
			payload = data[1:]
		elif func_code == Function.FUNC_R:
			what = data[0]
			if what != req[0]:
				raise NotImplementedError()
			payload = data[1:]
		elif func_code == Function.CTRL_W:
			payload = data
		elif func_code == Function.FUNC_W:
			what = data[0]
			if what != req[0]:
				raise NotImplementedError()
			payload = data[1:]
		elif func_code == Function.INV_FREQ_W:
			payload = data
		payload = int.from_bytes(payload, "big")

		logger.debug("Payload: %s", payload)
		return payload

def main():
	# Can start/stop but not change speed?

	logging.basicConfig(
	 level=logging.DEBUG,
	 format="%(levelname)s %(message)s"
	)

	ser = serial.Serial(port="/dev/ttyUSB0",
	 baudrate=9600,
	 parity=serial.PARITY_NONE,
	 bytesize=serial.EIGHTBITS,
	 stopbits=serial.STOPBITS_ONE,
	 timeout=1.0,
	)

	data = ser.read(5+2)

	logger.warning("Received %s",data.hex())

	vfd = VFD(ser)

	if 1:
		if 0:
			func_code = Function.INV_FREQ_W
			req = [0x37, 0x10]
		elif 0:
			"""
			So far, can run at 30 Hz but not more.
			Looks like we're only jogging.
			"""
			# ON
			func_code = Function.CTRL_W
			req = 0
			req |= 1<<ControlBit.RUN
			#req |= 1<<ControlBit.JOG
			#req |= 1<<ControlBit.JOGF
			req |= 1<<ControlBit.FOR
			#req |= 1 << ControlBit.STOP
			req = [req]
			# response but doesn't stop
		elif 0:
			"""
			So far, can run at 30 Hz but not more.
			Looks like we're only jogging.
			"""
			# ON
			func_code = Function.CTRL_W
			req = 0
			req |= 1<<ControlBit.RUN
			#req |= 1<<ControlBit.JOG
			req |= 1<<ControlBit.JOGF
			req |= 1<<ControlBit.FOR
			#req |= 1 << ControlBit.STOP
			req = [req]
			# response but doesn't stop

		elif 1:
			func_code = Function.CTRL_W
			req = 0
			req |= 1 << ControlBit.STOP
			req = [req]
			# response but doesn't stop

		elif 0:
			func_code = Function.STAT_R
			req = [ Status.SET_F ]
			# OK

		elif 0:
			func_code = Function.STAT_R
			req = [ Status.OUT_F ]
			# OK

		elif 0:
			func_code = Function.FUNC_W
			req = [ 0x03, 0x27, 0x10 ] # 100 @ 0.01 Hz
			# OK

		elif 0:
			func_code = Function.FUNC_R
			req = [ 0x03 ] # speed
			# OK
			# -> 01 01 03 03 0000 ccdd

		vfd.call(func_code, req)

	if 0:

		for x in range(256):
			if x in (12,22):
				continue # reserved
			try:
				res = vfd.call(Function.FUNC_R, [x])
				print(f"{x: 3d}: {res}")
			except Exception as e:
				print(f"{x: 3d}: NG ({e})")

if __name__ == "__main__":
	main()
