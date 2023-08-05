import usbtmc

class SCPI:
	def __init__(self, *args, **kw):
		self.args = args, kw

	def __enter__(self):
		args, kw = self.args
		self.s = usbtmc.Instrument(*args, **kw) # eg. 0x0699, 0x03aa

	def __exit__(self, exc_type, exc_value, exc_traceback):
		self.s.close()

	def ask(self, command):
		return self.s.ask(command)

	def write(self, command):
		return self.s.write(command)

	def read_raw(self, amount):
		return self.s.read_raw(amount)
