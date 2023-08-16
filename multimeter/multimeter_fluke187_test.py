import logging

import serial

from .multimeter_fluke187 import Multimeter


logger = logging.getLogger(__name__)


def test():
	ser = serial.Serial(port="/dev/ttyUSB0",
	 baudrate=9600,
	 parity=serial.PARITY_NONE,
	 bytesize=serial.EIGHTBITS,
	 stopbits=serial.STOPBITS_ONE,
	)
	with ser:
		with Multimeter(ser) as m:
			for i in range(5):
				v = m.measure_immediate()
				logger.info("v=%s", v)
