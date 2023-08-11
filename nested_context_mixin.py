#!/usr/bin/env python
# -*- coding: utf-8 vi:noet
# Mixin for having objects supporting nested context managers
# SPDX-FileCopyrightText: 2023 Jérôme Carretero <cJ@zougloub.eu>
# SPDX-License-Identifier: MIT

import logging

logger = logging.getLogger(__name__)


class NestedContextMixin:
	def __init__(self):
		self.__context_stack = []

	def init(self):
		raise NotImplementedError
		return self

	def exit(self, exc_type, exc_value, exc_traceback):
		raise NotImplementedError
		pass

	def add_context_info(self, init, exit):
		self.__context_stack.append((init, exit))
		return self

	def __enter__(self):
		logger.debug("Enter %s", self.__context_stack)

		if not self.__context_stack:
			self.__context_stack.append((self.init, self.exit))

		init, exit = self.__context_stack[-1]
		return init()

	def __exit__(self, exc_type, exc_value, exc_traceback):
		logger.debug("Exit %s", self.__context_stack)
		init, exit = self.__context_stack[-1]
		self.__context_stack = self.__context_stack[:-1]
		return exit(exc_type, exc_value, exc_traceback)


class Example(NestedContextMixin):
	def __init__(self):
		NestedContextMixin.__init__(self)

	def init(self):
		logger.info("Enter")
		return self

	def exit(self, exc_type, exc_value, exc_traceback):
		logger.info("Exit")
		pass

	def like_this(self):

		def init():
			logger.info("Enter current measurement")
			return self

		def exit(exc_type, exc_value, exc_traceback):
			logger.info("Exit current measurement")
			pass

		return self.add_context_info(init, exit)
