#!/usr/bin/env python
# -*- coding: utf-8 vi:noet
# Read codes form Symbol DS6708 in "Simple COM Port Emulation" mode
# SPDX-FileCopyrightText: 2018-2021 Jérôme Carretero <cJ@zougloub.eu>
# SPDX-License-Identifier: MIT


"""

Notes:

- In Simple COM Port emulation (HID) mode, in Linux the hidraw device
  file is root-owned unless the udev rule in this folder is loaded,
  and the user is in the plugdev group.

"""

import logging
import select
import io, os


logger = logging.getLogger(__name__)


def symbol_hidraw_find_first():
	"""
	Find the first hidraw device that looks like a Symbol barcode scanner

	TODO: add filtering capability

	::

	   DRIVER=hid-generic
	   HID_ID=0003:000005E0:00000600
	   HID_NAME=ﾩSymbol Technologies, Inc, 2002 Symbol Bar Code Scanner
	   HID_PHYS=usb-0000:00:14.0-4.4/input0
	   HID_UNIQ=S/N:... Rev:...
	   MODALIAS=hid:b0003g0001v000005E0p00000600

	"""
	hids = os.listdir("/sys/class/hidraw")
	hid = None
	for hid in hids:
		with io.open("/sys/class/hidraw/%s/device/uevent" % hid, "r") as f:
			data = f.read()
			#logger.debug("Data: %s", data)
			if "Symbol Bar Code Scanner" in data:
				break
	else:
		raise RuntimeError("Couldn't find a bar code scanner")
	return "/dev/%s" % hid


def symbol_hidraw_read(f) -> bytes:
	"""
	:return: Decoded bar code
	:param f: open HID file descriptor

	Notes:

	- The data is broken down in chunks of max. 64 bytes;
	  <= 63-byte chunks are prefixed by a length indicator, so they
	  can be reassembled.
	"""
	out = []
	while True:
		r, w, e = select.select([f], [], [], 0.1)
		if r == []:
			if len(out) == 0:
				continue
			else:
				# Assume we finished reading the code;
				# this may be problematic under high CPU load
				# for big codes
				break
		d = f.read(1)
		l = d[0]
		if l == 0:
			logger.warning("Unexpected 0-sized chunk?")
			continue
		chunk = f.read(l)
		logger.debug("Read chunk l=%d: %s", l, chunk.hex())
		out.append(chunk)
	return b"".join(out)
