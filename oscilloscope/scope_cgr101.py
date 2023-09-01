#!/usr/bin/env python
# -*- coding: utf-8 vi:noet
# Syscomp Electronic Design Ltd. Circuit Gear CGR-101
# A low-cost display-less multifunction scope

"""
2-channel, 20 Msps / 2 MHz, download rate 5/s
"""

import time
import logging

import numpy as np


logger = logging.getLogger(__name__)


class Scope:
	def __init__(self, ser):
		self.ser = ser
		self.adstepsize = [0,0]
		self._last_write = time.monotonic()
		self.scaler = [0,0]
		self.bias = [[0,0],[0,0]]
		self.gains = {
		 0: 0.00592, # "low"
		 1: 0.0521, # "high"
		}
		self._pos = 0

	def __enter__(self):

		self.ser.read(self.ser.inWaiting())
		time.sleep(0.1)
		self.ser.read(self.ser.inWaiting())

		id = self.identify()
		logger.info("id: %s", id)
		self.scale("A", 0)
		self.scale("B", 0)

		self._set_control_register(
		 sample_rate_div=1,
		 trigger_source=0,
		 trigger_polarity=0,
		 external_trigger=1,
		)

		return self

	def __exit__(self, exc_type, exc_value, exc_traceback):
		pass

	def _write(self, x):
		logger.debug("> %s", x)
		now = time.monotonic()
		DT = 0.001
		if now < self._last_write + DT:
			time.sleep(DT)
			now = time.monotonic()
		self.ser.write(x)
		self._last_write = now

	def _readline(self):
		logger.debug("? line")
		x = self.ser.readline()
		logger.debug("< %s", x)
		return x

	def _read(self, amount):
		logger.debug("? %d", amount)
		x = self.ser.read(amount)
		logger.debug("< %s", x[:64])
		return x

	def identify(self):
		self._write(b"i\n")
		return self._readline().rstrip()

	def _set_control_register(self,
	  sample_rate_div=None,
	  trigger_source=None,
	  trigger_polarity=None,
	  external_trigger=None,
	 ):
		if sample_rate_div is None:
			sample_rate_div = self.sample_rate_div
		if trigger_source is None:
			trigger_source = self.trigger_source
		if trigger_polarity is None:
			trigger_polarity = self.trigger_polarity
		if external_trigger is None:
			external_trigger = self.external_trigger
		val = (0
		 | sample_rate_div
		 | (trigger_source << 4)
		 | (trigger_polarity << 5)
		 | (external_trigger << 6)
		 )
		req = f"S R {val}\n".encode()
		self._write(req)

		if not external_trigger:
			self._write(b"S D 4\n")

		self.sample_rate_div = sample_rate_div
		self.trigger_source = trigger_source
		self.trigger_polarity = trigger_polarity
		self.external_trigger = external_trigger

	def set_frame_period(self, value):
		sample_period = value / 1024
		sample_rate = 1 / sample_period
		sample_rate = self.set_sample_rate(sample_rate)
		sample_period = 1 / sample_rate
		period = 1024 * sample_period
		return period

	def get_sample_rate(self):
		return self._sample_rate

	def set_sample_rate(self, value):
		for i in range(15, -1, -1):
			candidate = 20e6 / (2**i)
			logger.debug("Candidate %s want %s", candidate, value)
			if candidate > value:
				self._set_control_register(sample_rate_div=i)
				break
		logger.debug("Sample rate: %s", candidate)
		self._sample_rate = candidate
		return candidate

	def waveform_configure(self, freq=1000, noise=False):
		phase = int(round(freq / 0.09313225746))
		logger.debug("Phase: %f", phase)

		p0 = (phase >> 24) & 0xff
		p1 = (phase >> 16) & 0xff
		p2 = (phase >>  8) & 0xff
		p3 = (phase >>  0) & 0xff
		self._write(f"W F {p0} {p1} {p2} {p3}\n".encode())

		ampl = 255
		#ampl = 1
		self._write(f"W A {ampl}\n".encode())

		if 0:
			addr = np.arange(256)
			val = np.sin(2 * np.pi * addr / 256)
			val = np.int32(np.round(128 + val * 127))
			for a, v in zip(addr, val):
				req = f"W S {a} {v}\n".encode()
				self._write(req)

		self._write(b"W P\n")

		if noise:
			self._write(b"W N\n")
		else:
			self._write(b"W W\n")

	def scale(self, channel, high):
		"""
		"""
		high = int(high)
		self._write("S P {}\n".format(channel.upper() if high else channel.lower()).encode())
		idx_channel = ord(channel.lower())-ord("a")
		self.scaler[idx_channel] = high
		self.adstepsize[idx_channel] = self.gains[high]

	def set_post_trigger_sample_count(self, value):
		C_HIGH = (value >> 8)  & 0xff
		C_LOW = (value >> 0 ) & 0xff
		self._write(f"S C {C_HIGH} {C_LOW}\n".encode())

	def set_trigger_level(self, value):
		"""
		"""
		gain = 1 if self.scaler[self.trigger_source] == 1 else 10

		#value += self.bias[self.trigger_source][self.scaler[self.trigger_source]]
		value = int(round(511 - gain * value/0.052421484375))
		logger.debug("Threshold gain %s value %s", gain, value)
		T_HIGH = (value >> 8)  & 0xff
		T_LOW = (value >> 0 ) & 0xff
		self._write(f"S T {T_HIGH} {T_LOW}\n".encode())

	def trigger(self):
		"""
		Capture using external trigger
		"""
		if not self.external_trigger:
			self._set_control_register(external_trigger=1)

		logger.debug("Trigger?")
		self._write(b"S G\n")
		while True:

			self._write(b"S D 5\n")
			self._write(b"S D 4\n")

			sample_period = 1 / self._sample_rate
			period = 1024 * sample_period

			time.sleep(period * 0.1)

			self.ser.timeout = 0.1
			x = self._read(1)
			if not x:
				continue
			self.ser.timeout = None
			assert x == b"A", x
			logger.debug("Trigger! %s", x)
			d = self._read(2)
			self._pos = 1023-int.from_bytes(d, "big")
			logger.debug("Trigger! %s=%s", d, self._pos)
			break


	def capture(self):
		"""
		Capture using internal trigger
		"""
		self._write(b"S G\n")

		x = self._read(1)
		assert x == b"A", x
		logger.debug("Trigger! %s", x)
		d = self._read(2)
		self._pos = 1023-int.from_bytes(d, "big")
		logger.debug("Trigger! %s=%s", d, self._pos)


	def read_data_buffer(self):
		"""
		:return: an array for each channel
		Takes about 194 ms
		"""

		self._write(b"S B \n")
		x = self._read(1)
		assert x == b"D", x
		data = self._read(4096)
		arr = np.frombuffer(data, dtype=">H").reshape((-1, 2))

		arr = np.roll(arr, self._pos, axis=0)
		A, B = arr.T
		a = (511 - np.float32(A)) * self.adstepsize[0] - self.bias[0][self.scaler[0]]
		b = (511 - np.float32(B)) * self.adstepsize[1] - self.bias[1][self.scaler[1]] 
		return a, b

