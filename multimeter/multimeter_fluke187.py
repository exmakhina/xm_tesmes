#!/usr/bin/env python
# -*- coding: utf-8 vi:noet
# Multimeter implementation

"""
"""

import sys, io, os, subprocess
import logging
import time, datetime
import threading
import queue
import collections
import contextlib


logger = logging.getLogger(__name__)


class Multimeter():
	"""
	"""
	def __init__(self, ser):
		self.s = ser

	def __enter__(self):
		return self

	def __exit__(self, ext_type, exc_value, exc_traceback):
		pass

	def measure_immediate(self):
		self.s.write(b"QM\r")
		now = time.monotonic()
		code = self.s.read_until(b"\r")
		value = self.s.read_until(b"\r")
		logger.debug("code, value = %s, %s\r\n", code, value)
		res, mes = value.split(b",")
		value, unit = mes.split(b" ", 1)
		value = float(value)
		unit = unit.decode()
		factors = {
		 "n": 1e-9,
		 "u": 1e-6,
		 "m": 1e-3,
		 "k": 1e3,
		 "M": 1e6,
		}
		for k, v in factors.items():
			if unit.startswith(k):
				value *= v
				unit = unit[1:]
				break

		return now, value, unit
