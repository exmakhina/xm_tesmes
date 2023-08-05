
"""

# Enable ch2, then measure:
>>> ins.write("MEASUrement:MEAS2:TYPE MEAN")
>>> ins.ask("MEASUrement:MEAS2:VALue?")
'-4.78191301E-2'

"""


class Scope:
	def __init__(self, scpi):
		self.s = scpi

	def __enter__(self):
		self.s.ask("*IDN?")
		return self

	def __exit__(self, exc_type, exc_value, exc_traceback):
		pass

	def hardcopy(self) -> bytes:
		"""
		:return: bytes (BMP format)
		"""
		self.s.write("HARDCopy STARt")
		b = self.s.read_raw(400000)
		return b

	def curve(self) -> bytes:
		self.s.write("CURVE?")
		data = self.s.read_raw(400000)
		return data

	"WFMPre?"
	'2;16;BIN;RI;MSB;2500;"Ch2, DC coupling, 2.0E0 V/div, 5.0E-4 s/div, 2500 points, Sample mode";Y;2.0E-6;0;-1.67E-3;"s";3.125E-4;0.0E0;-2.2528E4;"Volts"'
