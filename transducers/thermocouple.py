#!/usr/bin/env python
# -*- coding: utf-8 vi:noet
# SPDX-FileCopyrightText: 2022 Jérôme Carretero <cJ@zougloub.eu>
# SPDX-License-Identifier: MIT
# Thermocouple (type K) temperature-emf relations

import sys, io, os
import logging

from .tabular import (
 bisect,
 forward,
 reverse,
)


logger = logging.getLogger(__name__)


TABLES = {}


def get_table(type):
	tab = os.path.join(os.path.dirname(__file__), "type_k.tab")

	table = {}
	with io.open(tab, "r", encoding="iso8859-15") as fi:
		for line in fi:
			line = line.strip()

			try:
				a, *b = line.split()
			except ValueError:
				continue

			logger.debug("Line: %s %s", a, b)

			if a == "°C":
				offsets = [ float(x) for x in  b ]
				continue

			try:
				int(a)
			except ValueError:
				continue

			if len(b) == 11:
				t = float(a)
				vals = [ float(x) for x in b ]
				logger.debug("Vals: %s", vals)
				for idx_val, val in enumerate(vals):
					table[t+offsets[idx_val]] = val

	return [ (k,v) for (k,v) in sorted(table.items()) ]


def temperature_to_emf_type_k(t_degC):
	table = TABLES.get("K")
	if table is None:
		table = TABLES["K"] = get_table("k")

	return forward(table, t_degC)


def emf_to_temperature_type_k(v):
	table = TABLES.get("K")
	if table is None:
		table = TABLES["K"] = get_table("k")

	return reverse(table, v)

