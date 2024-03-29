#!/usr/bin/env python
# -*- coding: utf-8 vi:noet
# Basic SCPI interface for TCP
# SPDX-FileCopyrightText: 2019-2023 Jérôme Carretero <cJ@zougloub.eu>
# SPDX-License-Identifier: MIT

import socket
import logging
import time
import contextlib

logger = logging.getLogger(__name__)

class SCPI(object):
	def __init__(self, endpoint, eol_tx=b"\r\n", eol_rx=b"\n"):
		self._endpoint = endpoint
		self._eol_tx = eol_tx
		self._eol_rx = eol_rx
		self._connect_attempts = 3

	def __str__(self):
		return "(SCPI_TCP)"

	def __enter__(self):
		logger.debug("%s enter", self)
		self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.sock.__enter__()
		for i in range(self._connect_attempts):
			try:
				self.sock.connect(self._endpoint)
				break
			except ConnectionRefusedError:
				time.sleep(1)
				if i == self._connect_attempts-1:
					raise

	def __exit__(self, exc_type, exc_value, exc_traceback):
		logger.debug("%s exit", self)
		self.sock.close()
		self.sock.__exit__(exc_type, exc_value, exc_traceback)

	def write(self, cmd):
		logger.debug("> %s", cmd)
		return self.sock.sendall(cmd.encode() + self._eol_tx)

	def read(self, n):
		a = bytearray()
		while len(a) != n:
			a += self.sock.recv(1)
		return bytes(a)

	def read_until(self, x):
		a = bytearray()
		while not a.endswith(x):
			a += self.sock.recv(1)
		return bytes(a)

	def ask(self, cmd):
		self.write(cmd)
		res = self.read_until(self._eol_rx).rstrip().decode('ascii')
		logger.debug("< %s", res)
		return res
