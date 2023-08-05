#!/usr/bin/env python
# -*- coding: utf-8 vi:noet
# Userspace driver for the Korad KA3305P programmable power supply

import sys, time
import serial
import logging

logger = logging.getLogger(__name__)

class PSU(object):
	def __init__(self, ser):
		self._serial = ser

	def __enter__(self):
		self.cmd("*IDN?")
		return self

	def __exit__(self, exc_type, exc_value, exc_tb):
		pass

	def cmd(self, cmd, timeout=0.1, l=None):
		"""
		Send a generic command to the PSU.

		:param cmd: the command to send (string)
		:param timeout: timeout to wait for (s) if l is unspecified
		:param l: expected length of result

		Note: when l is supplied, the command is retried until the result
		has the right length.
		"""
		ser = self._serial
		if l is None:
			logger.debug("> %s", cmd.encode())
			ser.write(cmd.encode())
			time.sleep(timeout)
			x = ser.read(ser.in_waiting)
			logger.debug("< %s", x.hex())
		else:
			while True:
				logger.debug("> %s", cmd.encode())
				ser.write(cmd.encode())
				timeout = ser.timeout
				ser.timeout = 1.0
				x = ser.read(l)
				logger.debug("< %s", x)
				ser.timeout = timeout
				if len(x) != l:
					sys.stderr.write("Warning, no response from meter\n")
				else:
					break
		return x

	def idn(self):
		return self.cmd("*IDN?")


	def getvalue(self, word, l=5):
		"""
		Retrieve a value from the PSU

		:param word: the word to read (eg. "ISET1?")
		:param l: length of return value if not default

		Note: currently {I,V}{SET,OUT}{1,2} all use l=5.
		"""
		if not word.endswith("?"):
			word = word + "?"

		return float(self.cmd(word, l=l))

	def setvalue(self, word, value):
		"""
		Set a value

		:param word: the word to set (eg. "ISET1")
		:param value: the value to set it to
		"""
		fmt = {
		 "ISET1": "%5.3f",
		 "ISET2": "%5.3f",
		 "VSET1": "%5.2f",
		 "VSET2": "%5.2f",
		}[word]
		self.cmd("%s:%s" % (word, fmt % value))

	def set_on(self, doit=True):
		self.cmd("OUT%d" % doit, l=None)

	def lock(self, doit=True):
		self.cmd("LOCK%d" % doit, l=None)

	def print_status(self):
		"""
		TODO
		"""
		#out1 = self.getvalue("OUT1?")
		iset1 = self.getvalue("ISET1?")
		vset1 = self.getvalue("VSET1?")
		iout1 = self.getvalue("IOUT1?")
		vout1 = self.getvalue("VOUT1?")
		iset2 = self.getvalue("ISET2?")
		vset2 = self.getvalue("VSET2?")
		iout2 = self.getvalue("IOUT2?")
		vout2 = self.getvalue("VOUT2?")
		print("VSET1=%.2f ISET1=%.3f VOUT1=%.2f IOUT1=%.3f" \
		 % (vset1, iset1, vout1, iout1))
		print("VSET2=%.2f ISET2=%.3f VOUT2=%.2f IOUT2=%.3f" \
		 % (vset2, iset2, vout2, iout2))

def main():

	import argparse

	parser = argparse.ArgumentParser(
	 description="Test",
	)

	parser.add_argument("--log-level",
	 default="INFO",
	 help="Logging level (eg. INFO, see Python logging docs)",
	)

	parser.add_argument("--serial-port",
	 help="",
	)

	subparsers = parser.add_subparsers(
	 help='the command; type "%s COMMAND -h" for command-specific help' % sys.argv[0],
	 dest='command',
	)


	subp = subparsers.add_parser(
	 "power",
	 help="Configure power",
	)

	subp.add_argument("state",
	 type=int,
	 choices=(0,1),
	)

	def do_power(psu, args):
		psu.set_on(args.state)

	subp.set_defaults(func=do_power)

	try:
		import argcomplete
		argcomplete.autocomplete(parser)
	except:
		pass

	args = parser.parse_args()

	logging.root.setLevel(getattr(logging, args.log_level))

	logging.basicConfig(
		format="%(levelname)s %(message)s"
	)


	if getattr(args, 'func', None) is None:
		parser.print_help()
		return 1
	else:
		if args.serial_port is None:
			args.serial_port = "/dev/serial/by-id/usb-USB_Vir_USB_Virtual_COM_NT2009101400-if00"

		ser = serial.Serial(
		 port=args.serial_port,
		 baudrate=9600,
		 bytesize=serial.EIGHTBITS,
		 parity=serial.PARITY_NONE,
		 stopbits=serial.STOPBITS_ONE,
		 timeout=0.1,
		 xonxoff=False,
		)

		with ser:
			with PSU(ser) as psu:
				args.func(psu, args)
		return 0

	s = PSU()
	#s.test()
	idn = s.idn()
	print(idn)
	while True:
		s.print_status()
		time.sleep(1)

	raise SystemExit()

	s.setvalue("VSET1", 5.00)
	s.setvalue("ISET1", 1.0)
	s.setvalue("VSET2", 0.00)
	s.setvalue("ISET2", 0.0)

	time.sleep(1)
	s.print_status()


if __name__ == '__main__':
	ret = main()
	raise SystemExit(ret)
