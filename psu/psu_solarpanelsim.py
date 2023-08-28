#!/usr/bin/env python
# -*- coding: utf-8 vi:noet
# PSU wrapper to act like a solar panel
# SPDX-FileCopyrightText: 2023 Jérôme Carretero <cJ@zougloub.eu> & contributors
# SPDX-License-Identifier: MIT

import logging
import threading
import time


logger = logging.getLogger(__name__)


class SolarPanel:
	def __init__(self, psu, ivcurve, ocv, cci):
		"""
		:param ivcurve: callable returning i(v)
		:param ocv: open-circuit (max) voltage
		:param cci: closed-circuit (max) current
		"""

		self.psu = psu
		self._iv = ivcurve
		self._ocv = ocv
		self._cci = cci
		self._dt = 1

	def __enter__(self):
		self.running = True
		self.t = threading.Thread(target=self.run)
		self.t.start()
		return self

	def __exit__(self, exc_type, exc_value, exc_tb):
		self.running = False
		self.t.join()

	def run(self):
		"""
		"""

		while self.running:
			try:
				self.step()
				time.sleep(self._dt)
			except KeyboardInterrupt:
				logger.info("Keyboard interrupt")
				break
			except Exception as e:
				logger.exception("Unexpected error: %s", e)
				break

	def step(self):
		"""
		"""
		psu = self.psu

		v_set = psu.voltage_setpoint_get()
		i_set = psu.current_setpoint_get()
		v_mes = psu.sense_voltage()
		i_mes = psu.sense_current()

		logger.debug("V = %f (%f)", v_mes, v_set)
		logger.debug("I = %f (%f)", i_mes, i_set)

		i_ref = self._iv(v_mes)
		logger.debug("I(%f) = %f", v_mes, i_ref)

		logger.debug("I = %f", i_mes)

		i_err = i_ref - i_mes
		logger.debug("Error: %f", i_err)

		cc = abs(v_set-v_mes) < 0.01
		if cc:
			Kp = 5
			v_new = min(v_set + Kp * i_err, self._ocv)
			logger.debug("Command V=%f", v_new)
			psu.voltage_setpoint_set(v_new)
		else:
			Kp = 0.5
			i_new = min(i_set + Kp * i_err, self._cci)
			logger.debug("Command I=%f", i_new)
			psu.current_setpoint_set(i_new)
