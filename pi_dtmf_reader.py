'''
  pi_dtmf_reader.py
  
  Copyright 2021 Guilhem Tiennot
  
  GPIO reading, and conversion of the MT8870 output to string.
  
  Dependencies: RPi.gpio
  
  This file is part of MyIVR.
  
  MyIVR is free software: you can redistribute it and/or modify
  it under the terms of the GNU General Public License as published by
  the Free Software Foundation, either version 3 of the License, or
  (at your option) any later version.
  
  MyIVR is distributed in the hope that it will be useful,
  but WITHOUT ANY WARRANTY; without even the implied warranty of
  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
  GNU General Public License for more details.
  
  You should have received a copy of the GNU General Public License
  along with MyIVR.  If not, see <https://www.gnu.org/licenses/>.
'''

from RPi import GPIO

class PiDtmfReader:
	SINGLE_CHAR_OUTPUT=1
	LITTERAL_OUTPUT=0
	INHIBIT=GPIO.HIGH
	NO_INHIBIT=GPIO.LOW
	
	OUTPUT_ARRAYS=[['D','1','2','3','4','5','6','7','8','9','0','star','hash','A','B','C'],
	['D','1','2','3','4','5','6','7','8','9','0','*','#','A','B','C']]
	
	DATA_PINS=[25,8,7,1] # From MSB to LSB
	TRIGGER_PIN=15
	INHIBIT_PIN=14
	
	def __init__(self, output_mode=SINGLE_CHAR_OUTPUT, inhibit_mode=NO_INHIBIT, callback=None):
		self.set_output_mode(output_mode)
		GPIO.setmode(GPIO.BCM)
		for i in self.DATA_PINS:
			GPIO.setup(i, GPIO.IN)
		GPIO.setup(self.INHIBIT_PIN, GPIO.OUT, initial=inhibit_mode)
		GPIO.setup(self.TRIGGER_PIN, GPIO.IN)
		GPIO.add_event_detect(self.TRIGGER_PIN, GPIO.FALLING, callback=self._trigger)
		
		self._index_val = None
		self._callback = callback
	
	def _trigger(self, channel):
		digit = ""
		
		for i in self.DATA_PINS:
			if GPIO.input(i) == GPIO.HIGH:
				digit += "1"
			else:
				digit += "0"
		
		self._index_val = int(digit,2)
		
		if self._callback and hasattr(self._callback,'__call__'):
			self._callback()
	
	def read(self):
		return self._output_array[self._index_val]
	
	def set_output_mode(self, output_mode):
		self._output_array = self.OUTPUT_ARRAYS[output_mode]
	
	def set_inhibit_mode(self, inhibit_mode):
		GPIO.output(self.INHIBIT_PIN, inhibit_mode)
	
	def __del__(self):
		GPIO.cleanup()

if __name__ == '__main__':
	try:
		def callback_print():
			print("Key pressed: '%s'" % (piDtmf.read()))
			
		piDtmf = PiDtmfReader(callback=callback_print)
		
		while True:
			pass
		
	except KeyboardInterrupt as e:
		del piDtmf
