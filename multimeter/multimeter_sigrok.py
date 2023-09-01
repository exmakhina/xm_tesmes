#!/usr/bin/env python
# -*- coding: utf-8 vi:noet
# Multimeter implementation for sigrok multimeters

"""

References:

- https://github.com/karlp/sigrok-python-example/blob/master/sr-read-methods.py

"""

import sys, io, os, subprocess
import re
import logging
import time, datetime
import threading
import queue
import collections


logger = logging.getLogger(__name__)


class Multimeter():
	"""
	"""
	def __init__(self, dev="eevblog-121gw:conn=bt/ble122/88-6B-0F-81-AA-48"):
		self.cmd = f"sigrok-cli -d {dev} --continuous".split()
		self.queues = collections.defaultdict(queue.Queue)

	def __enter__(self):
		self.running = True
		self.t = threading.Thread(target=self.run)
		self.t.start()
		return self

	def __exit__(self, exc_type, exc_value, exc_traceback):
		self.running = False
		self.t.join()

	def run(self):
		env = {}
		env.update(os.environ)
		env["LC_ALL"] = "C"

		with subprocess.Popen(self.cmd, stdout=subprocess.PIPE, env=env) as proc:

			while self.running:
				logger.debug("Run?")
				if proc.poll() is not None:
					break
				x = proc.stdout.readline()
				if not x:
					break
				x = x.decode("utf-8").strip()
				t = time.monotonic()
				logger.debug("< %s", x)
				m = re.match(r"^(?P<k>\S+): (?P<v>\S+)(\s+(?P<u>\S+)(\s+(?P<x>.*))?)?$", x)
				assert m is not None
				k = m.group("k")
				v = float(m.group("v"))
				try:
					u = m.group("u")
				except KeyError:
					u = None
				self.queues[k].put((t, v, u))

			proc.stdout.close()
			logger.info("term")
			proc.wait()
			logger.info("term!")
			self.running = False

		logger.info("done")

	def get_data(self, key):
		while self.running:
			try:
				v = self.queues[key].get(block=True, timeout=1)
			except queue.Empty:
				continue
			return v

	def measure_immediate(self):
		v = None
		while self.running:
			try:
				v = self.queues["main"].get(block=True, timeout=1)
			except queue.Empty as e:
				if v is not None:
					break
		return v
