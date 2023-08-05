#!/usr/bin/env python
# -*- coding: utf-8 vi:noet
# Multimeter implementation for the Fluke network multimeter

import time, socket, re, datetime, sys
import logging

"""

Multimeter is

References:

- http://websrv.mece.ualberta.ca/electrowiki/images/b/b5/8845a_Programmers_Manual.pdf

"""

logger = logging.getLogger(__name__)


class Multimeter():
	"""
	"""
	def __init__(self, scpi):
		self.s = scpi

	def __enter__(self, **kw):
		"""
			Performs initialization of the meter.
		"""
		return self

	def __exit__(self, type, exc, tb):
		logger.debug("OK")
		#return super().__exit__(type, exc, tb)

	def init_remote(self):
		a = self.s.write("SYST:REM")

	def init_local(self):
		a = self.s.write("SYST:LOC")

	def get_both(self):
		l = self.s.ask("INIT; FETCH1?; FETCH2?")
		m = re.match(r"(?P<i>\S+);(?P<v>\S+)", l)
		assert m is not None
		return float(m.group("i")), float(m.group("v"))

	def get_one(self):
		l = self.s.ask("INIT; FETCH1?")
		m = re.match(r"(?P<i>\S+)", l)
		assert m is not None
		return float(m.group("i"))

	def fetch(self, function=1):
		l = self.s.ask(f"FETCH{function}?")
		return [float(x) for x in l.split(",")]

	def get_ohms(self):
		a = self.s.ask("MEAS:RES?")
		b = re.match(r"^'(\S+?)(\r\n)?'$", a)
		c = b.group(1)
		logger.debug("c =",c)
		res = float(c)
		#except ValueError:# as e:
		#		print "Error, value " + a + " not correct"
		#		time.sleep(1)

		logger.debug("res =", res, "ohm")
		time.sleep(.2)
		return res

	def get_volts(self, rng=100):
		a = self.s.ask("MEAS:VOLT:DC? %d" % rng)
		a = a.strip().replace("+", "").replace("'", "")
		res = float(a)
		return res

	def get_amps(self):
		a = self.s.ask("MEAS:CURR:DC?")
		#print(a)
		a = a.strip().replace("+", "").replace("'", "")
		res = float(a)
		return res

