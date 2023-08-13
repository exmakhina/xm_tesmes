#!/usr/bin/env python
# -*- coding: utf-8 vi:noet
# PSU implementation for KORAD KEL-103 Programmable Electronic load
# SPDX-FileCopyrightText: 2023 Jérôme Carretero <cJ@zougloub.eu>
# SPDX-License-Identifier: MIT

import logging
import io
import os
import contextlib


with io.open(os.path.join(os.path.dirname(__file__), "load_korad_kel103.rst"), "r") as fi:
	__doc__ = fi.read()


logger = logging.getLogger(__name__)


class Load:
	def __init__(self, scpi):
		self.scpi = scpi

	def __enter__(self):
		idn = self.scpi.ask("*IDN?")
		logger.info("IDN: %s", idn)
		return self

	def __exit__(self, exc_type, exc_value, exc_traceback):
		pass

	def setpoint_set(self, value):
		"""
		Configure setpoint (depending on present mode)
		"""
		self.scpi.write(f":{self._func} {value:.3f}{self._unit}")

	def setpoint_get(self):
		"""
		Obtain setpoint (depending on present mode)
		"""
		return float(self.scpi.ask(f":{self._func}?")[:-len(self._unit)])

	def create_measure(kw, unit):
		def get(self):
			f"""
			Measure {unit}
			"""
			return float(self.scpi.ask(f":MEAS:{kw}?")[:-len(unit)])
		return get

	measure_i = create_measure("CURR", "A")
	measure_u = create_measure("VOLT", "V")
	measure_p = create_measure("POW", "W")

	def _set_mode(self, func):
		self.scpi.write(f":FUNC {func}")
		func_rb = self.scpi.ask(":FUNC?")
		if func_rb != func:
			raise RuntimeError()

	@contextlib.contextmanager
	def backup_and_restore_func(self):
		func_old = self.scpi.ask(":FUNC?")
		yield self
		if func_old == "CONTINUOUS CV":
			self.scpi.ask(":DYN?")
		else:
			self._set_mode(func_old)

	def create_mode(mode, kw, unit):
		@contextlib.contextmanager
		def in_mode(self):
			with self.backup_and_restore_func():
				self._set_mode(mode)
				self._func = kw
				self._unit = unit
				yield self
		return in_mode

	in_cc = create_mode("CC", "CURR", "A")
	in_cv = create_mode("CV", "VOLT", "V")
	in_cr = create_mode("CR", "RES", "OHM")
	in_cw = create_mode("CW", "POW", "W")

	def save(self, index: int):
		self.scpi.write(f"*SAV {index}")

	def recall(self, index: int):
		self.scpi.write(f"*RCL {index}")

	def activate(self, doit):
		self.scpi.write(f":INP {1 if doit else 0}")

	def activated(self):
		v = self.scpi.ask(":INP?")
		return {"OFF": False, "ON": True}[v]

	def trigger(self):
		self.scpi.write("*TRG")

	@contextlib.contextmanager
	def in_dynamic_cv(self, setpoint_a, setpoint_b, frequency, dutycycle):
		"""
		Configure dynamic CV mode

		:param frequency: inverse period of infinite cycle to perform
		:param dutycycle: ratio of second setpoint duration over total duration
		"""
		with self.backup_and_restore_func():
			self.scpi.write(f":DYN 1,{setpoint_a}V,{setpoint_b}V,{frequency}HZ,{dutycycle*100}%")
			self.scpi.ask(":DYN?")
			yield self
			self.scpi.write(":INP 0")
