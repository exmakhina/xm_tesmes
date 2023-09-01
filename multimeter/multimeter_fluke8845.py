#!/usr/bin/env python
# -*- coding: utf-8 vi:noet
# Multimeter implementation for the Fluke network multimeter

import io
import os
import time, socket, re, datetime, sys
import logging

from ..nested_context_mixin import NestedContextMixin


with io.open(__file__.replace(".py", ".rst"), "r") as fi:
	__doc__ = fi.read()


logger = logging.getLogger(__name__)


class Multimeter(NestedContextMixin):
	"""
	"""
	def __init__(self, scpi):
		NestedContextMixin.__init__(self)
		self.scpi = scpi

	def init(self):
		"""
			Performs initialization of the meter.
		"""
		idn = self.scpi.ask("*IDN?")
		return self

	def exit(self, exc_type, exc_value, exc_tb):
		pass

	def in_remote(self):
		def init():
			self.init_remote()
			return self
		def exit(exc_type, exc_value, exc_traceback):
			# Can't go back
			self.init_local()
		return self.add_context_info(init, exit)

	def in_local(self):
		def init():
			self.init_local()
			return self
		def exit(exc_type, exc_value, exc_traceback):
			# Can't go back
			self.init_local()
		return self.add_context_info(init, exit)

	def init_remote(self):
		logger.info("Enter remote control")
		a = self.scpi.write("SYST:REM")

	def init_local(self):
		logger.info("Enter local control")
		a = self.scpi.write("SYST:LOC")

	def streaming_read(self):
		"""
		Perform raw stream reading that was initiated using READ?,
		giving max. 50k measurements.
		"""
		self.scpi.write("READ?")
		while True:
			try:
				v = self.scpi.read(15)
				t = time.monotonic()
				if v[0] == ord(","):
					v = v[1:] + self.scpi.read(1)
				ret = float(v)
				if ret > 1e37:
					ret = float("NaN")
				yield t, ret
			except KeyboardInterrupt:
				self.scpi.write("")
				break

	def immediate_read(self):
		"""
		Perform single reading, using *TRG and READ?
		"""
		self.scpi.write("*TRG")
		t = time.monotonic()
		ret = self.scpi.ask("READ?")
		ret = float(v)
		if ret > 1e37:
			ret = float("NaN")
		yield t, ret

	def get_both(self):
		l = self.scpi.ask("INIT; FETCH1?; FETCH2?")
		m = re.match(r"(?P<i>\S+);(?P<v>\S+)", l)
		assert m is not None
		return float(m.group("i")), float(m.group("v"))

	def get_one(self):
		l = self.scpi.ask("INIT; FETCH1?")
		m = re.match(r"(?P<i>\S+)", l)
		assert m is not None
		return float(m.group("i"))

	def fetch(self, function=1):
		l = self.scpi.ask(f"FETCH{function}?")
		return [float(x) for x in l.split(",")]

	def get_ohms(self):
		a = self.scpi.ask("MEAS:RES?")
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
		a = self.scpi.ask("MEAS:VOLT:DC? %d" % rng)
		a = a.strip().replace("+", "").replace("'", "")
		res = float(a)
		return res

	def get_amps(self):
		a = self.scpi.ask("MEAS:CURR:DC?")
		#print(a)
		a = a.strip().replace("+", "").replace("'", "")
		res = float(a)
		return res

