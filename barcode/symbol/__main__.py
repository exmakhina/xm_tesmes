#!/usr/bin/env python
# -*- coding: utf-8 vi:noet
# Perform some testing on Symbol DS6708
# SPDX-FileCopyrightText: 2021 Jérôme Carretero <cJ@zougloub.eu>
# SPDX-License-Identifier: MIT


import logging
import sys, io, os, subprocess, logging, struct, codecs, time, select


logger = logging.getLogger(__name__)


def main():

	import argparse

	parser = argparse.ArgumentParser(
	 description="Symbol Barcode Reader Tool",
	)

	parser.add_argument("--log-level",
	 default="INFO",
	 help="Logging level (eg. INFO, see Python logging docs)",
	)

	subparsers = parser.add_subparsers(
	 help='the command; type "%s COMMAND -h" for command-specific help' % sys.argv[0],
	 dest='command',
	)


	subp = subparsers.add_parser(
	 "read-hid",
	 help="Read from reader in HID mode",
	)

	def do_read_hid(args):
		from .hid import (
		 symbol_hidraw_find_first,
		 symbol_hidraw_read,
		)
		devpath = symbol_hidraw_find_first()
		with io.open(devpath, "rb") as f:
			s = symbol_hidraw_read(f)
			sys.stdout.buffer.write(s)
			sys.stdout.buffer.flush()

	subp.set_defaults(func=do_read_hid)


	subp = subparsers.add_parser(
	 "read-cdc",
	 help="Read from reader in HID mode",
	)

	def do_read_cdc(args):
		import serial
		from .cdc import (
		 symbol_cdc_read,
		)
		ser = serial.Serial(
		 port="/dev/ttyACM0",
		 bytesize=serial.EIGHTBITS,
		 parity=serial.PARITY_NONE,
		 #stopbit
		)

		with ser as fi:#with io.open("/dev/ttyACM0", "rb") as fi:
			s = symbol_cdc_read(fi)
			sys.stdout.buffer.write(s)
			sys.stdout.buffer.flush()

	subp.set_defaults(func=do_read_cdc)


	try:
		import argcomplete
		argcomplete.autocomplete(parser)
	except:
		pass

	args = parser.parse_args()

	logging.basicConfig(
	 datefmt="%Y%m%dT%H%M%S",
	 level=getattr(logging, args.log_level),
	 format="%(asctime)-15s %(name)s %(levelname)s %(message)s"
	)

	if getattr(args, 'func', None) is None:
		parser.print_help()
		return 1
	else:
		return args.func(args)

if __name__ == "__main__":
	ret = main()
	raise SystemExit(ret)
