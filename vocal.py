'''
  vocal.py
  
  Copyright 2021 Guilhem Tiennot
  
  Text-to-speech module.
  
  Dependencies: pyaudio, threading, subprocess, wave, os, sys,
				SVoxPico (TTS software, see `readme.md` for installation
				instructions)
  
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

import subprocess
from os import remove,path
from sys import argv
import pyaudio
import wave
import threading

TMP_FILENAME=path.join(path.dirname(argv[0]),"tmp.wav")
CHUNK=1024

class Vocal():
	def __init__(self, sound_device_index=None, sample_rate=16000, lang="fr-FR"):
		self._p = pyaudio.PyAudio()
		self._s = self._p.open(format=pyaudio.paInt16, channels=1,
		rate=sample_rate, output=True,
		output_device_index=sound_device_index)
		self._stopped = True
		self._file_locked = False
		self._lang = lang
	
	def _playfile(self):
		self._stopped = False
		self._file_locked = True
		wf = wave.open(TMP_FILENAME, 'rb')
		data = wf.readframes(CHUNK)
		self._s.start_stream()
		while data and not self._stopped:
			self._s.write(data)
			data = wf.readframes(CHUNK)
		wf.close()
		remove(TMP_FILENAME)
		self._s.stop_stream()
		self._stopped = True
		self._file_locked = False
	
	def play(self, text):
		while self._file_locked:
			pass
		
		pico = subprocess.run(["pico2wave","-l",self._lang,"-w",TMP_FILENAME,text])
		pico.check_returncode()
		self._t = threading.Thread(target=self._playfile)
		self._t.daemon = True
		self._t.start()
	
	def stop(self):
		self._stopped = True
	
	def is_playing(self):
		return not self._stopped
	
	def __del__(self):
		self._p.terminate()
