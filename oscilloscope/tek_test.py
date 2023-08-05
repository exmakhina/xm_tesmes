import logging
import io

from ..scpi.usbtmc import SCPI
from .tek import Scope


logger = logging.getLogger(__name__)


def test():
	scpi = SCPI(0x0699, 0x03aa)

	with scpi:
		scope = Scope(scpi)

		if 1:
			# TODO
			curve = scope.curve()
			logger.info("curve: %s", curve)

		if 1:
			logger.debug("Harcopy?")
			bmp = scope.hardcopy()
			logger.info("bmp %s", len(bmp))
			with io.open("scope.bmp", "wb") as fo:
				fo.write(bmp)
