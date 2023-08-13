#!/usr/bin/env python
# -*- coding: utf-8 vi:noet
# PSU implementation for KORAD KEL-103 Programmable Electronic load
# SPDX-FileCopyrightText: 2023 Jérôme Carretero <cJ@zougloub.eu>
# SPDX-License-Identifier: MIT

import io
import os

with io.open(os.path.join(os.path.dirname(__file__), "load_korad_kel103.rst"), "r") as fi:
	__doc__ = fi.read()
