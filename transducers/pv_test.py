import logging

import sympy
import numpy as np
import matplotlib
import matplotlib.figure
import matplotlib.backend_bases
import scipy.constants

from .pv import *

logger = logging.getLogger(__name__)


def test_pv():

	if 0:
		log = sympy.log
		exp = sympy.exp
	else:
		exp = np.exp
		log = np.log

	q = scipy.constants.e
	k = scipy.constants.k

	N = 50
	T = 300
	V_t = (scipy.constants.k  * T / scipy.constants.e)

	if 0:
		N_s = 1
		n = 1.3
		I_0 = 1e-12  # Diode reverse saturation current in amperes
		R_s = 0.1  # Series resistance in ohms
		R_sh = 1000  # Shunt resistance in ohms
		V_oc = 0.7
		I_sc = 5.0
	else:
		# SPR-MAX3-375-BLK
		N_s = 104
		V_mpp = 64
		I_mpp = 5.86
		I_sc = 6.30
		V_oc = 75.5

		if 1:
			V_mpp /= N_s
			V_oc /= N_s
			N_s = 1

		# https://en.wikipedia.org/wiki/Saturation_current
		I_ph = I_sc  # Photogenerated current in amperes
		I_0 = 1e-12
		n = V_oc / N_s / (V_t * log(I_ph / I_0 + 1))
		#I_0 = I_ph / (exp(V_oc / (n * V_t)) - 1)

		# Basic modeling...
		R_sh = V_mpp / (I_sc - I_mpp)
		R_s = (V_oc - V_mpp) / I_mpp

	logger.info("n = %f", n)
	logger.info("R_s = %f Ohm", R_s)
	logger.info("R_sh = %f Ohm", R_sh)
	logger.info("I_0 = %f nA", I_0 * 1e9)
	logger.info("V_t = %f mV", V_t * 1e3)

	V = np.linspace(1e-3, V_oc, N)  # Voltage array from 0V to 40V
	I = solar_panel_iv(V, I_ph=I_sc, I_0=I_0, R_s=R_s, R_sh=R_sh, T=T, n=n, N_s=N_s)
	if 0:
		I = []
		for v in V:
			i = solar_panel_iv(v, I_ph=I_sc, I_0=I_0, R_s=R_s, R_sh=R_sh, T=T, n=n, N_s=N_s)
			I.append(i)

	subpcfg = matplotlib.figure.SubplotParams(
	 left  =0.10,
	 bottom=0.10,
	 right =0.90,
	 top   =0.90,
	 wspace=0.00,
	 hspace=0.00,
	)
	figure = matplotlib.figure.Figure(
	 facecolor='white',
	 edgecolor='white',
	 subplotpars=subpcfg,
	)

	figure.set_figheight(8)
	figure.set_figwidth(12)
	figure.set_dpi(72)

	axes = figure.add_subplot(1, 1, 1)

	axes.xaxis.grid(True)
	axes.yaxis.grid(True)
	axes.set_xlabel("Voltage (V)")
	axes.set_ylabel("Current (I)")
	axes.plot(V, I, ".-")

	title = "Solar Panel I(V) curve"
	figure.suptitle(title)

	out_dir = "."
	base = "test-pv"
	for ext in ("svg", "png", "pdf"):
		canvas_class = matplotlib.backend_bases.get_registered_canvas_class(ext)
		figure_canvas = canvas_class(figure)
		canvas_print = getattr(figure_canvas, 'print_%s' % ext)
		canvas_print("%s.%s" % (base, ext))

