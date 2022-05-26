#!/usr/bin/env python
# -*- coding: utf-8 vi:noet
# RTD (PT100) temperature-resistance relations
# SPDX-FileCopyrightText: 2022 Jérôme Carretero <cJ@zougloub.eu>
# SPDX-License-Identifier: MIT

import logging


logger = logging.getLogger(__name__)


# IEC 60751:2022
# Callendar-Van Dusen equation
TABLES = {
 "PT-385": {
  (-200, 0): {
   "R0": 100.0000,
   "A": 3.9083E-3,
   "B": -5.775E-7,
   "C": -4.183E-12,
  },
  (0, 650): {
   "R0": 100.0000,
   "A": 3.9083E-3,
   "B": -5.775E-7,
   "C": 0,
  },
 }
}

def temperature_to_r(t_degC, rtd_tc="PT-385"):

	table = TABLES[rtd_tc]
	#logger.info("table: %s", table)
	for (a, b), coefs in table.items():
		if a <= t_degC <= b:
			break

	R0 = coefs["R0"]
	A = coefs["A"]
	B = coefs["B"]
	C = coefs["C"]
	t = t_degC

	return R0 * (1 + A * t + B * t**2 + C * (t-100) * (t**3))


def r_to_temperature(r, rtd_tc="PT-385"):
	table = TABLES[rtd_tc]
	for (a, b), coefs in table.items():
		break

	R0 = coefs["R0"]
	A = coefs["A"]
	B = coefs["B"]
	C = coefs["C"]

	t = (-A+(A**2 - 4 * B * (1 - r / R0))**0.5) / (2*B)

	return t
