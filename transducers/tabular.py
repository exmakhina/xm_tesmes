#!/usr/bin/env python
# -*- coding: utf-8 vi:noet


import logging


logger = logging.getLogger(__name__)


def bisect(a, target, get):
	logger.debug("Looking for %s", target)
	lo = 0
	hi = len(a)

	while hi - lo > 1:
		mid = (lo+hi) // 2
		v = get(a[mid])
		if logger.isEnabledFor(logging.DEBUG):
			v_lo = get(a[lo])
			try:
				v_hi = get(a[hi])
			except:
				v_hi = None
			logger.debug("Currently at %d..%d %s..%s %s", lo, hi, v_lo, v_hi, v)

		if target > v:
			logger.debug("Narrowing down to RHS")
			lo = mid
		else:
			logger.debug("Narrowing down to LHS")
			hi = mid

	logger.debug("Narrowed it down to %s-%s (%s-%s)", lo, hi, get(a[lo]), get(a[hi]))
	return lo, hi


def forward(table, value):
	pa, pb = bisect(table, value, lambda x: x[0])
	ta, va = table[pa]
	tb, vb = table[pb]
	assert ta <= value <= tb
	return va + (value - ta) * (vb - va) / (tb - ta)


def reverse(table, value):
	pa, pb = bisect(table, value, lambda x: x[1])
	ta, va = table[pa]
	tb, vb = table[pb]
	assert va <= value <= vb
	return ta + (value - va) * (tb - ta) / (vb - va)

