#!/usr/bin/env python
# -*- coding: utf-8 vi:noet
# Userspace driver for Symbol DS6708 in "CDC Host" mode
# SPDX-FileCopyrightText: 2018-2021 Jérôme Carretero <cJ@zougloub.eu>
# SPDX-License-Identifier: MIT

"""

Notes:

- In CDC mode, the serial port must be open in raw mode (this
  __main__ does it)

- In CDC mode, the DS6708 doesn't provide its S/N.
  When many readers are used, use /dev/serial/by-path


"""

import logging
import select


logger = logging.getLogger(__name__)


def symbol_cdc_read(f):
	"""
	Read a code in CDC mode
	"""

	out = []
	while True:
		r, w, e = select.select([f], [], [], 0.1)
		if r == []:
			if len(out) == 0:
				continue
			elif out[-2:] == [b"\x0d", b"\x0a"]:
				logger.debug("End of code")
				break
			else:
				logger.warning("Unexpected timeout")

		d = f.read(1)
		if not d:
			logger.warning("Unexpected broken pipe")
			break

		out.append(d)

	return b"".join(out[:-2])

