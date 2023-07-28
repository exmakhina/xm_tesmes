#!/usr/bin/env python
# -*- coding: utf-8 vi:noet
# PSU implementation for Keysight E3633A and E3634A

"""
The notable thing about this PSU is the serial port quirkiness:

- DTE port, so a null-modem cable has to be used 99% of the time
- 9600 bps max speed
- 2 stop bits
- hardware control flow, and with dsr/dtr
"""

import logging

logger = logging.getLogger(__name__)


class PSU:
	"""
	"""
	def __init__(self, scpi: "SCPI"):
		"""
		:param scpi: probably a ..scpi.serial.SCPI object
		"""
		self.s = scpi

	def __enter__(self):
		idn = self.s.ask("*IDN?")
		logger.info("IDN: %s", idn)
		assert idn.startswith("HEWLETT-PACKARD,E3634A,"), f"Unknown PSU {idn}!"
		return self

	def __exit__(self, ext_type, exc_value, exc_traceback):
		pass

	def enable(self, doit=True):
		self.s.write("OUT {}".format("ON" if doit else "OFF"))

	def voltage_setpoint_get(self):
		return float(self.s.ask(":VOLT?"))

	def voltage_setpoint_set(self, value):
		self.s.write(f":VOLT {value}")

	def current_setpoint_get(self):
		return float(self.s.ask(f":CURR?"))

	def current_setpoint_set(self, value):
		self.s.write(f":CURR {value}")

	def sense_voltage(self):
		return float(self.s.ask("MEAS:VOLT?"))

	def sense_current(self):
		return float(self.s.ask("MEAS:CURR?"))

	def sense_both(self):
		return self.sense_voltage(), self.sense_current()

	def measure_immediate(self):
		a, b, c = self.s.ask("MEAS?").split(",")
		return a


def main(argv=None):
	import argparse
	import contextlib

	parser = argparse.ArgumentParser(
	 description="PSU helper",
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
	 baudrate=9600,
	 parity=serial.PARITY_NONE,
	 bytesize=serial.EIGHTBITS,
	 stopbits=serial.STOPBITS_TWO,
	 dsrdtr=True,
	)

	import time

	with ser:
		with SCPI(ser, eol=b"\n") as scpi:
			with PSU(scpi) as psu:

				vref = psu.voltage_setpoint_get()
				logger.info("V: %f", vref)
				iref = psu.current_setpoint_get()
				logger.info("I: %f", iref)

				ts = []
				vus = []
				vis = []
				for idx_step in range(10):
					u, i = psu.sense_both()
					t = time.time()
					ts.append(t)
					vus.append(u)
					vis.append(i)

			import matplotlib
			import matplotlib.figure
			import matplotlib.patches
			import matplotlib.mlab as mlab
			import matplotlib.backend_bases

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
			color = 'tab:blue'
			axes.set_ylabel("Voltage (V)", color=color)
			axes.plot(ts, vus, label="U", color=color)
			axes.tick_params(axis="y", labelcolor=color)
			axes.set_ylim((0, 5))

			ax2 = axes.twinx()
			color = 'tab:red'
			ax2.set_ylabel("Current (A)", color=color)
			ax2.plot(ts, vis, color=color)
			ax2.tick_params(axis="y", labelcolor=color)
			ax2.set_ylim((0, 2))

			#axes.legend()

			title = "Sample plot"
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
