import logging
import time

import serial
import numpy as np
import pytest

from .circuitgear_cgr101 import Scope


logger = logging.getLogger(__name__)

logging.getLogger("matplotlib.font_manager").setLevel(logging.INFO)


@pytest.fixture
def scope():
	ser = serial.Serial(port="/dev/serial/by-id/usb-Syscomp_CircuitGear_CGS8R4DH-if00-port0",
	 baudrate=230400,
	 parity=serial.PARITY_NONE,
	 bytesize=serial.EIGHTBITS,
	 stopbits=serial.STOPBITS_ONE,
	)
	with ser:
		with Scope(ser) as s:
			yield s


def plot(scope, name, title=""):
	a0, b0 = scope.read_data_buffer()
	t = np.arange(1024) / scope.get_sample_rate()

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
	axes.set_xlabel("Time (s)")
	axes.set_ylabel("Voltage (V)")

	axes.plot(t, a0, ".", label="A")
	axes.plot(t, b0, ".", label="B")

	axes.legend()

	figure.suptitle(title)

	out_dir = "."
	base = f"test-{name}"
	for ext in ("svg", "png", "pdf"):
		canvas_class = matplotlib.backend_bases.get_registered_canvas_class(ext)
		figure_canvas = canvas_class(figure)
		canvas_print = getattr(figure_canvas, 'print_%s' % ext)
		canvas_print("%s.%s" % (base, ext))


def test_triggerext_min_freq(scope):
	scope.scale("A", 0)
	scope.scale("B", 0)
	scope.waveform_configure(noise=True)

	sp = scope.set_frame_period(5)
	logger.info("Capture period: %s", sp)

	scope._set_control_register(external_trigger=1)
	scope.trigger()

	plot(scope, "trig_ext_min_freq")


def test_triggerint_min_freq(scope):
	scope.scale("A", 0)
	scope.scale("B", 0)
	scope.waveform_configure(noise=True)

	sp = scope.set_frame_period(0.5)
	sp = scope.set_frame_period(2.5)
	logger.info("Capture period: %s", sp)

	scope.set_trigger_level(0.0)
	scope.set_post_trigger_sample_count(1023)
	scope._set_control_register(external_trigger=0)
	scope.capture()

	plot(scope, "trig_int_min_freq")


def test_data_buffer_read_speed(scope):
	t0 = time.monotonic()
	a1, b1 = scope.read_data_buffer()
	t1 = time.monotonic()
	logger.info("Buffer read in %f s", t1-t0)


def test_calibration(scope):
	s = scope
	s.scale("A", 0)
	s.scale("B", 0)

	def calib0():
		s.bias = [[0.038,0.0521], [0.015,-0.0521]]

	calib0()

	# TODO

def test_refresh_rate(scope):
	scope.scale("A", 0)
	scope.scale("B", 0)
	scope.waveform_configure(noise=False)
	sp = scope.set_frame_period(0.0001)
	logger.info("Capture period: %s", sp)

	n = 10
	t0 = time.monotonic()
	for i in range(n):
		scope.trigger()
		a, b = scope.read_data_buffer()
	t1 = time.monotonic()

	logger.info("Read %d frames in %f s, ie. %f frame/s", n, t1-t0, n/(t1-t0))


def test_tk(scope):
	scope.scale("A", 0)
	scope.scale("B", 0)
	scope.waveform_configure(noise=False)
	sp = scope.set_frame_period(0.01)
	logger.info("Capture period: %s", sp)
	import matplotlib.pyplot as plt
	from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
	import tkinter as tk
	import numpy as np

	class Application(tk.Frame):
		def __init__(self, master=None):
			tk.Frame.__init__(self,master)
			self.createWidgets()

		def createWidgets(self):
			fig=plt.figure(figsize=(8,8))
			ax=fig.add_axes([0.1,0.1,0.8,0.8])
			canvas=FigureCanvasTkAgg(fig,master=root)
			canvas.get_tk_widget().grid(row=0,column=1)
			canvas.draw()
			self.canvas = canvas
			self.ax = ax
			self.plots = [
			 ax.plot([], [], label="A")[0],
			 ax.plot([], [], label="B")[0],
			]
			ax.set_xlim(0, sp)
			ax.set_ylim(-1,1)

			scope.trigger()
			self.after(1, self.refresh)

		def refresh(self):
			a, b = scope.read_data_buffer()
			scope.trigger()
			t = np.arange(1024) / scope.get_sample_rate()
			self.plots[0].set_xdata(t)
			self.plots[0].set_ydata(a)
			self.plots[1].set_xdata(t)
			self.plots[1].set_ydata(b)
			self.canvas.draw()

			self.after(1, self.refresh)

	root=tk.Tk()
	app=Application(master=root)
	app.mainloop()
