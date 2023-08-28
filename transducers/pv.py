import logging

if 0:
	import sympy
	log = sympy.log
	exp = sympy.exp
	lambertw = sympy.LambertW
else:
	import numpy as np
	exp = np.exp
	log = np.log
	import scipy.special
	def lambertw(x):
		return abs(scipy.special.lambertw(x))

import scipy.constants


logger = logging.getLogger(__name__)


def solar_panel_iv(V, I_ph, I_0, R_s, R_sh, T, n=1, N_s=1):
	"""
	Calculate the current I based on the voltage V for a solar panel using the single-diode model.

	:param P: power (after efficiency)
	:param V: Voltage across the solar panel terminals
	:param I_0: Diode reverse (dark) saturation current
	:param R_s: Series resistance
	:param R_sh: Shunt resistance
	:param V_t: Thermal voltage
	:param n: diode ideality factor

	:return: Current flowing through the solar panel
	:rtype: float or numpy.ndarray
	"""

	q = scipy.constants.e
	k = scipy.constants.k

	V_t = k  * T / q

	a = n * V_t * N_s


	if 0:
		# Diode only
		I = I_ph - I_0 * (exp(q*V/(n*k*T))-1)
		return I

	elif 0:
		# Diode + shunt
		I = I_ph - I_0 * (exp(q*V/(n*k*T))-1) - V/R_sh
		return I

	elif 1:
		# https://arxiv.org/pdf/2307.08099.pdf
		# One can obtain an explicit expression for I using the Lambert W function [3]

		bigexp = exp((R_sh * (R_s * (I_ph + I_0) + V))/(a * (R_sh + R_s)))
		I = (
		   1 / (R_sh + R_s) * (R_sh * (I_ph + I_0) - V)
		 - (a / R_s) * lambertw(((I_0 * R_sh * R_s)/(a * (R_sh + R_s))) * bigexp)
		)
	else:
		# https://arxiv.org/pdf/2307.08099.pdf
		# Eq. 2 can be rewritten in terms of the LogWright function as:

		def g(x):
			return x - lambertw(exp(x))

		u = (
		   log((I_0 * R_s * R_sh)/(a * (R_s + R_sh)))
		 + (R_s * R_sh * (I_ph + I_0) + V * R_sh) / (a * (R_sh + R_s))
		)

		I = (
		   (a / R_s) * (g(u) - log((I_0 * R_s) / (a * (1 + R_s/R_sh))))
		 - V/R_s
		)

	if isinstance(I, np.ndarray):
		np.clip(I, 0, I_ph, out=I)
	else:
		if I < 0:
			I = 0

		if I > I_ph:
			I = I_ph

	return I
