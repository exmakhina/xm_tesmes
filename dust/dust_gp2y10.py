#!/usr/bin/env python
# -*- coding: utf-8 vi:noet
# SPDX-FileCopyrightText: 2020 Jérôme Carretero <cJ@zougloub.eu>
# SPDX-License-Identifier: MIT

"""

This is a userspace driver for the Sharp GP2Y1010AU0F dust density sensor

References:

- https://www.sparkfun.com/datasheets/Sensors/gp2y1010au_e.pdf
- https://www.mouser.com/catalog/additional/Sharp_Microelectronics_Application_Guide_for_Sharp_GP2Y1026AU0F_Dust_Sensor.pdf
- https://global.sharp/products/device/lineup/data/pdf/datasheet/gp2y1010au_appl_e.pdf
  https://github.com/esaid/GP2Y1010AU0F-DUST-Sensor/blob/master/gp2y1010au_appl_e.pdf

"""

import sys
import re
import serial
import logging
import struct

logger = logging.getLogger(__name__)

class Dust_GP2Y10(object):
	def __init__(self, port="/dev/ttyUSB0", offset=0.9, sensitivity=0.005):
		"""
		:param offset: Output voltage at no dust, defaults to typical
		:param sensitivity: sensitivity in V / (ug/m3), defaults to typical
		"""
		self._port = port
		self._offset = offset
		self._gain =  1 / sensitivity
		self._serial = ser

	def __enter__(self):
		self._serial = ser = serial.Serial()
		ser.baudrate = 9600
		ser.port = self._port
		ser.timeout = 60
		ser.open()
		return self

	def __exit__(self, *args):
		self._serial.close()

	def read(self):
		ret = dict()

		while True:
			data = self._serial.read_until(b"\r")
			if data.startswith(b"CanKao"):
				continue
			m = re.match(rb"u=(\S+)V\n\r", data)
			if m is None:
				logger.warning("Ignored %s", data)
				continue
			u = float(m.group(1))
			ret["u"] = u
			ret["PM_ug_m3"] = (u - self._offset) * self._gain
			return ret

def recalibrate():
	"""
	Figure out original calibration parameters from the module
	"""

	data = """
u=0.48V
CanKao:0.025 mg/m3
u=0.54V
CanKao:0.035 mg/m3
u=0.56V
CanKao:0.040 mg/m3
u=0.48V
CanKao:0.025 mg/m3
u=0.52V
CanKao:0.032 mg/m3
u=0.51V
CanKao:0.030 mg/m3
u=0.49V
CanKao:0.027 mg/m3
u=0.47V
CanKao:0.022 mg/m3
u=0.55V
CanKao:0.038 mg/m3
u=0.55V
CanKao:0.037 mg/m3
u=0.55V
CanKao:0.037 mg/m3
u=0.51V
CanKao:0.031 mg/m3
u=0.53V
CanKao:0.034 mg/m3
u=0.54V
CanKao:0.036 mg/m3
u=0.49V
CanKao:0.026 mg/m3
""".strip()

	lines = data.splitlines()

	us = list()
	pms = list()
	import re
	for a, b in zip(lines[0::2], lines[1::2]):
		print(a, b)
		ma = re.match("u=(\S+)V", a)
		mb = re.match("CanKao:(\S+) mg/m3", b)
		u = float(ma.group(1))
		pm = float(mb.group(1))
		print(u, pm)
		us.append(u)
		pms.append(pm)

	import numpy as np
	import scipy.optimize

	us = np.array(us, dtype=np.float64)
	pms = np.array(pms, dtype=np.float64)


	def fit(params):
		offset, gain = params
		return (us - offset) * gain

	def residue(params):
		mes = pms
		calc = fit(params)
		return (mes - calc)**2


	params = (0.5, 0.1)

	plsq = scipy.optimize.leastsq(residue,
	 params,
	 full_output=True,
	)

	ret = scipy.optimize.OptimizeResult(
	 x=plsq[0],
	 cov_x=plsq[1],
	 message=plsq[3],
	 status=plsq[4],
	)
	ret.update(plsq[2])

	print(ret)
	print(residue(ret.x))


if __name__ == '__main__':

	if 0:
		recalibrate()
		raise SystemExit()

	import datetime

	with Dust_GP2Y10(offset=0.43, sensitivity=0.005) as s:
		while True:
			rec = s.read()
			now = datetime.datetime.now()
			sys.stdout.write("- time: %s\n" % (now.strftime("%Y-%m-%dT%H:%M:%S.%f")))
			for k, v in rec.items():
				sys.stdout.write("  %s: %s\n" % (k, v))
			sys.stdout.flush()
