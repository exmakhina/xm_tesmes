#!/usr/bin/env python
# -*- coding: utf-8 vi::noet

import struct, time
import usb

VIDPIDS = [
 (0x0c45, 0x7401),
]
REQ_INT_LEN = 8
ENDPOINT = 0x82
CONFIG_NO = 1
TIMEOUT = 5000
USB_PORTS_STR = '^\s*(\d+)-(\d+(?:\.\d+)*)'
USB_SYS_PREFIX = '/sys/bus/usb/devices/'
COMMANDS = {
 'temp': '\x01\x80\x33\x01\x00\x00\x00\x00',
 'ini1': '\x01\x82\x77\x01\x00\x00\x00\x00',
 'ini2': '\x01\x86\xff\x01\x00\x00\x00\x00',
}

class TemperDevice(object):
	"""
	A TEMPer USB thermometer.
	"""
	def __init__(self, device):
		self._gain = 1.0/256
		self._bias = -3.7
		self._device = device
		self._bus = device.bus
		self._ports = getattr(device, 'port_number', None)
		if self._device.is_kernel_driver_active:
			for interface in [0, 1]:
				try:
					self._device.detach_kernel_driver(interface)
				except usb.core.USBError:
					pass
			self._device.set_configuration(1)
			self._device.ctrl_transfer(
			 bmRequestType=0x21, bRequest=0x09,
			 wValue=0x0201, wIndex=0x00, data_or_wLength='\x01\x01',
			 timeout=TIMEOUT)
		
		#self._device.reset()
		#time.sleep(0.1)
		
		self._control_transfer(COMMANDS['temp'])
		self._interrupt_read()
		self._control_transfer(COMMANDS['ini1'])
		self._interrupt_read()
		self._control_transfer(COMMANDS['ini2'])
		self._interrupt_read()
		self._interrupt_read()

	def get_temp_degC(self):
		self._control_transfer(COMMANDS['temp'])
		data = self._interrupt_read()
		if not (data[0] == 128 and data[1] == 2 \
		 and data[4] == 101 and data[5] == 114 \
		 and data[6] == 70 and data[7] == 49):
			raise RuntimeError("Unexpected interrupt contents: %s" % (data))
		return self._gain * struct.unpack(">h", data[2:4])[0] + self._bias

	def _control_transfer(self, data):
		self._device.ctrl_transfer(bmRequestType=0x21, bRequest=0x09,
		 wValue=0x0200, wIndex=0x01, data_or_wLength=data, timeout=TIMEOUT)

	def _interrupt_read(self):
		return self._device.read(ENDPOINT, REQ_INT_LEN, timeout=TIMEOUT)


class TemperHandler(object):
	"""
	Handler for TEMPer USB thermometers.
	"""

	def __init__(self):
		self._devices = []
		for vid, pid in VIDPIDS:
			self._devices += [TemperDevice(device) for device in \
				usb.core.find(find_all=True, idVendor=vid, idProduct=pid)]

	def get_devices(self):
		"""
		Get a list of all devices attached to this handler
		"""
		return self._devices


if __name__ == '__main__':
	import sys, io, time, datetime

	th = TemperHandler()
	tempers = th.get_devices()
	assert len(tempers) == 1, tempers
	sensor = tempers[0]

	class DataLog(object):
		def __init__(self):
			pass
			#self._file = io.open("temp.tsv", "wb")
		def __del__(self):
			pass
			#self._file.close()
		def log(self, x):
			if not isinstance(x, bytes):
				x = x.encode()
			#self._file.write(x)
			sys.stdout.write(x)
			sys.stdout.flush()

	l = DataLog()

	while True:
		now = datetime.datetime.now()
		t = sensor.get_temp_degC()
		ts = now.strftime("%Y%m%dT%H%M%S.%f")
		l.log("%s\t%.4f\n" % (ts, t))
		#rem = now.microsecond
		#time.sleep(1.0 - rem*1e-6)
		time.sleep(60)

