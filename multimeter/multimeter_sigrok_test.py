import logging

from .multimeter_sigrok import *

logger = logging.getLogger(__name__)


def test():
	with Multimeter() as meter:
		while True:
			res = meter.measure_immediate()
			if res is None:
				break

			t, v, u = res
			logger.info("%s: %s %s", t, v, u)
