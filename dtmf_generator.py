'''
  dtmf_generator.py
  
  Copyright 2021 Guilhem Tiennot
  
  Function for dialing a phone number, with DTMF.
  
  Dependencies: sys, (tty, termios for Unix-like), numpy, pyaudio
  
  This file is part of My202Modem.
  
  My202Modem is free software: you can redistribute it and/or modify
  it under the terms of the GNU General Public License as published by
  the Free Software Foundation, either version 3 of the License, or
  (at your option) any later version.
  
  My202Modem is distributed in the hope that it will be useful,
  but WITHOUT ANY WARRANTY; without even the implied warranty of
  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
  GNU General Public License for more details.
  
  You should have received a copy of the GNU General Public License
  along with My202Modem.  If not, see <https://www.gnu.org/licenses/>.
'''

import sys
import numpy as np
import pyaudio

if sys.platform in ('linux','darwin'):
	import tty, termios


'''
	DTMF Frequencies
	
	
	         1209Hz  1336Hz  1477Hz  1633Hz
	697Hz       1       2       3       A
	770Hz       4       5       6       B
	852Hz       7       8       9       C
	941Hz       *       0       #       D

'''

DTMF_FREQS = {'1': (697, 1209), '2': (697,1336), '3': (697,1477), 'A': (697, 1633),
'4': (770, 1209), '5': (770, 1336), '6': (770, 1477), 'B': (770, 1633),
'7': (852, 1209), '8': (852, 1336), '9': (852, 1477), 'C': (852, 1633),
'*': (941, 1209), '0': (941, 1336), '#': (941, 1477), 'D': (941, 1633)}

DIGIT_DURATION = 0.25

def dtmf_compose(dial_number, pyaudio_stream, volume=1, sample_rate=44100):
	s_number = int(DIGIT_DURATION*sample_rate)
	blank = np.zeros(s_number).astype(np.float32)
	pyaudio_stream.write(blank, s_number)
	
	for digit in dial_number:
		if digit in DTMF_FREQS.keys():
			freq1 = float(DTMF_FREQS[digit][0])
			freq2 = float(DTMF_FREQS[digit][1])
			
			samples = np.zeros(s_number).astype(np.float32)
			for i in range(s_number):
				samples[i] = float(volume*(np.sin(2*np.pi*i*freq1/sample_rate))
				+(np.sin(2*np.pi*i*freq2/sample_rate))) / 2
			
			pyaudio_stream.write(samples, s_number)
			pyaudio_stream.write(blank, s_number)

if __name__ == '__main__':
	try:
		if sys.platform in ('linux','darwin'):
			settings = termios.tcgetattr(sys.stdin.fileno())
			tty.setcbreak(sys.stdin.fileno())
		p = pyaudio.PyAudio()
		s = p.open(format=pyaudio.paFloat32, channels=1, rate=44100, output=True)
		
		while True:
			c = sys.stdin.read(1)
			print(c)
			dtmf_compose(c,s,volume=0.5)
		
	except KeyboardInterrupt as e:
		s.close()
		p.terminate()
		if sys.platform in ('linux','darwin'):
			termios.tcsetattr(sys.stdin.fileno(), termios.TCSADRAIN, settings)
		pass
