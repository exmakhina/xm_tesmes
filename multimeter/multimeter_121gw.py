#!/usr/bin/env python
# -*- coding: utf-8 vi:noet
# Multimeter implementation for the 121GW multimeter
# dead code -> use sigrok

import sys, io, os, subprocess, re, codecs
import time, datetime

"""

References:

- Revised packet format blob v2
  
"""

class EEV_121GW():
	"""
	"""
	def __init__(self):
		pass

	def get_data(self):
		cmd = ["gatttool", "-b", "88:6B:0F:81:AA:48", "--char-read", "--handle=0x0007"]
		out = subprocess.check_output(cmd).rstrip().decode()
		print(out)
		m = re.match(r"^Characteristic value/descriptor: (.*)$", out)
		assert m is not None, out
		data = m.groups()[0]
		print(data)
		blob = codecs.decode(data.replace(" ", ""), "hex")
		print(blob)


def test():
	f = EEV_121GW()
	d = f.get_data()
	print(d)
	if 0:
		for x in range(5):
			r = f.get_volts()
			print("Tension: %.3f V" % (r))
			r = f.get_amps()
			print("Courant: %.3f A" % (r))
	if 0:
		while True:
			ts = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
			i_a, u_v = f.get_both()
			sys.stdout.write("%s;%9.6f;%9.6f;%9.6f\n" % (ts, u_v, i_a, i_a * u_v))
			sys.stdout.flush()

if __name__ == '__main__':
	test()


