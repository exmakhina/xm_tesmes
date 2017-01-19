#!/usr/bin/env python
# -*- coding: utf-8 vi:noet
# Multimeter implementation for the Fluke network multimeter

import time, socket, re, datetime, sys

"""

References:

- http://websrv.mece.ualberta.ca/electrowiki/images/b/b5/8845a_Programmers_Manual.pdf

"""


class Fluke():
	"""
	"""
	def __init__(self):
		pass

	def init(self, **kw):
		"""
			Performs initialization of the meter.
		"""
		host = '192.168.1.122'
		if "host" in kw:
			host = kw["host"]
		self.HOST = host

		port = 3490
		if "port" in kw:
			port = kw["port"]
		self.PORT = port

		self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		#print "Connecting...",
		self.sock.connect((self.HOST, self.PORT))
		#print "OK"
		self.init_remote()

	def cmd_send(self,command):
		#print "Sending " + command + "...",
		self.sock.send(command + "\r")
		#print "OK"

	def recv(self, **kw):
		if "timeout" in kw:
			self.sock.settimeout(kw["timeout"])
		else:
			self.sock.settimeout(0.5)
		try:

			#print "Receiving...",
			data = self.sock.recv(1024)
			#print "OK"
		except:
			#print "Timeout."
			data = None
		
		#print 'Received : ', repr(data)
		return repr(data)

	def readline(self, timeout=2):
		res = b""
		while True:
			try:
				x = self.sock.recv(1)
			except socket.error as e:
				if e.errno == 11:
					continue
				else:
					raise
			res = res + x
			if res.endswith(b"\r\n"):
				return res

	def init_remote(self):
		a = self.cmd_send("SYST:REM")

	def init_local(self):
		a = self.cmd_send("SYST:LOC")

	def get_both(self):
		self.cmd_send("INIT; FETCH1?; FETCH2?")
		l = self.readline()
		m = re.match(r"(?P<i>\S+);(?P<v>\S+)", l)
		assert m is not None
		return float(m.group("i")), float(m.group("v"))

	def get_ohms(self):
		a = self.recv(timeout=0)
		a = self.recv(timeout=0)
		self.cmd_send("MEAS:RES?")
		a = self.recv()
		b = re.match(r"^'(\S+?)(\r\n)?'$", a)
		c = b.group(1)
		#print "c =",c
		res = float(c)
		#except ValueError:# as e:
		#		print "Error, value " + a + " not correct"
		#		time.sleep(1)

		#print "res =", res, "ohm"
		time.sleep(.2)
		return res

	def get_volts(self, rng=100):
		a = self.recv(timeout=0)
		self.cmd_send("MEAS:VOLT:DC? %d" % rng)
		a = self.readline()
		#print(a)
		a = a.strip().replace("+", "").replace("'", "")
		res = float(a)
		return res

	def get_amps(self):
		a = self.recv(timeout=0)
		self.cmd_send("MEAS:CURR:DC?")
		a = self.readline(timeout=2)
		#print(a)
		a = a.strip().replace("+", "").replace("'", "")
		res = float(a)
		return res

	def close(self):
		#print "Closing...",
		self.sock.close()
		#print "OK"

def test():
	f = Fluke()
	f.init(host='192.168.0.131')
	#f.init_remote()
	if 0:
		for x in range(5):
			r = f.get_volts()
			print("Tension: %.3f V" % (r))
			r = f.get_amps()
			print("Courant: %.3f A" % (r))
	if 1:
		while True:
			ts = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
			i_a, u_v = f.get_both()
			sys.stdout.write("%s;%9.6f;%9.6f;%9.6f\n" % (ts, u_v, i_a, i_a * u_v))
			sys.stdout.flush()
	f.init_local()
	f.close()

if __name__ == '__main__':
	test()


