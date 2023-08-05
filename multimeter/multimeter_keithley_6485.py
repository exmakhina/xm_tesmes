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
	def __init__(self, scpi):
		self.s = scpi

	def __enter__(self):
		self.s.ask("*IDN?")
		return self

	def __exit__(self, ext_type, exc_value, exc_traceback):
		pass

	def measure_immediate(self):
		a, b, c = self.s.ask("MEAS?").split(",")
		return a


def main(argv=None):
	import argparse

	parser = argparse.ArgumentParser(
	 description="Multimeter helper",
	)

	parser.add_argument("--log-level",
	 default="INFO",
	 help="Logging level (eg. INFO, see Python logging docs)",
	)

	try:
		import argcomplete
		argcomplete.autocomplete(parser)
	except:
		pass

	args = parser.parse_args(argv)

	logging.basicConfig(
	 datefmt="%Y%m%dT%H%M%S",
	 level=getattr(logging, args.log_level),
	 format="%(asctime)-15s %(name)s %(levelname)s %(message)s"
	)

	import serial
	from exmakhina.tesmes.scpi.serial import SCPI

	# Configure using CONFIG > COMM
	ser = serial.Serial(port="/dev/ttyUSB0",
	 baudrate=57600,
	 parity=serial.PARITY_NONE,
	 bytesize=serial.EIGHTBITS,
	 stopbits=serial.STOPBITS_ONE,
	)

	with ser:
		with SCPI(ser, eol=b"\n") as scpi:
			with Multimeter(scpi) as meter:
				x = meter.measure_immediate()

			for line in """
*RST
FORM:ELEM READ,TIME # configure to receive timestamps
TRIG:DEL 0
TRIG:COUN 2000
NPLC .01            # fast
RANG .002
SYST:ZCH OFF
SYST:AZER:STAT OFF
DISP:ENAB OFF
*CLS
TRAC:POIN 2000
TRAC:CLE
TRAC:FEED:CONT NEXT
STAT:MEAS:ENAB 512
*SRE 1
*OPC?
INIT
DISP:ENAB ON
TRAC:DATA?
""".strip().splitlines():
				if "#" in line:
					line = line.split("#")[0].strip()
				if line.endswith("?"):
					logger.debug("> %s", line)
					res = scpi.ask(line)
					logger.debug("< %s", line)
				else:
					logger.debug("> %s", line)
					scpi.write(line)

			print(res)

			import matplotlib
			import matplotlib.figure
			import matplotlib.patches
			import matplotlib.mlab as mlab
			import matplotlib.backend_bases

			import numpy as np

			ys, xs = np.array([float(x) for x in res.split(",")]).reshape((-1, 2)).T

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
			axes.set_xlabel("Time")
			axes.set_ylabel("Current")

			axes.plot(xs, ys, label="")

			axes.legend()

			title = "Plot"
			figure.suptitle(title)

			out_dir = "."
			base = "plot"
			for ext in ("svg", "png", "pdf"):
				canvas_class = matplotlib.backend_bases.get_registered_canvas_class(ext)
				figure_canvas = canvas_class(figure)
				canvas_print = getattr(figure_canvas, 'print_%s' % ext)
				canvas_print("%s.%s" % (base, ext))


if __name__ == "__main__":
	ret = main()
	raise SystemExit(ret)
