#!/usr/bin/env python
# -*- coding: utf-8 vi:noet
# Basic SCPI interface for serial port

import logging
import serial

logger = logging.getLogger(__name__)


class SCPI(object):
	"""
	"""
	def __init__(self, ser, eol=b"\r\n"):
		self.ser = ser
		self.eol = eol
		if not self.ser.is_open:
			raise RuntimeError('Communication initialization failed!')

	def __enter__(self):
		return self

	def __exit__(self, exc_type, exc_value, exc_traceback):
		pass

	def readline(self):
		line = b""
		while True:
			a = self.ser.read(1)
			line += a
			if line.endswith(self.eol):
				break
		return line

	def write(self, cmd):
		logger.debug("> %s", cmd)
		return self.ser.write("{}".format(cmd).encode('ascii') + self.eol)

	def ask(self, cmd):
		logger.debug("> %s", cmd)
		self.ser.write("{}".format(cmd).encode('ascii') + self.eol)
		res = self.readline().rstrip().decode('ascii')
		logger.debug("< %s", res)
		return res

