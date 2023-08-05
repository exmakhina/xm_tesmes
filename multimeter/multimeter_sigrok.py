#!/usr/bin/env python
# -*- coding: utf-8 vi:noet
# Multimeter implementation for sigrok multimeters

"""

References:

- https://github.com/karlp/sigrok-python-example/blob/master/sr-read-methods.py

"""

import sys, io, os, subprocess
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

	def __exit__(self, *args):
		self.running = False
		self.t.join()

	def run(self):
		env = {}
		env.update(os.environ)
		env["LC_ALL"] = "C"

		with subprocess.Popen(self.cmd, stdout=subprocess.PIPE, env=env) as proc:

			while self.running:
				if proc.poll() is not None:
					break
				x = proc.stdout.readline()
				if not x:
					break
				x = x.decode("utf-8").strip()
				logger.debug("< %s", x)
				t = time.time()
				k, vu = x.split(":", 1)
				try:
					v, u = vu.split()[:2]
				except ValueError:
					v = vu
				self.queues[k].put((t, float(v)))

			proc.terminate()

	def get_data(self, key):
		v = self.queues[key].get()
		return v


def main(argv=None):
	import argparse

	parser = argparse.ArgumentParser(
	 description="Factory programming tool",
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

	with (
	  Multimeter() as f,
	  io.open("oven.yml", "a") as fo,
	 ):
		while True:
			t, v = f.get_data("main")
			fo.write(f"- t: {t}\n")
			fo.write(f"  t_degC: {v}\n")
			fo.flush()

if __name__ == "__main__":
	ret = main()
	raise SystemExit(ret)
