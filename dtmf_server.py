'''
  dtmf_server.py
  
  Copyright 2021 Guilhem Tiennot
  
  A simple interactive voice response implementation. Designed to run
  on a Raspberry Pi 2 (and later models) with the GPIO port, and
  a DTMF module based on the MT8870 chip.
  
  Dependencies: configparser, pyaudio, threading, RPi.gpio, time, subprocess,
				wave, os, sys, SVoxPico (TTS software, see `readme.md`
				for installation instructions)
  
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


import configparser as cp
from sys import argv, stdin
from os.path import isfile
from time import sleep, time
from vocal import Vocal
from pi_dtmf_reader import PiDtmfReader

GLOBAL_SECTION='global'
ENTRY_POINT_KEY='start'
SPEECH_KEY='speech'
DEFAULT_KEY='default'
EXIT_CMD='exit'
RESET_CMD='reset'
MEMCLEAR_CMD='memclear'

ALLOWED_KEYS=(SPEECH_KEY,'hash','star','0','1','2','3','4','5','6','7','8','9',DEFAULT_KEY)
ALLOWED_CMDS=(EXIT_CMD,RESET_CMD,MEMCLEAR_CMD)

TIMEOUT=5
SAFETY_DELAY=1

key_detected = False
last_detect_ts = 0

def read_pressed_key():
	global key_detected
	global last_detect_ts
	
	if time()-last_detect_ts > SAFETY_DELAY:
		key_detected = True
		last_detect_ts = time()


if len(argv) != 2:
	print("Usage: %s <config.ini>" % (argv[0]))
	exit(1)

if not isfile(argv[1]):
	raise FileExistsError("File '%s' not found." % (argv[1]))

conf = cp.ConfigParser()
conf.read(argv[1])

voc = Vocal()
pi_dtmf = PiDtmfReader(output_mode=PiDtmfReader.LITTERAL_OUTPUT, callback=read_pressed_key)

if not GLOBAL_SECTION in conf:
	raise SyntaxError("Missing '%s' section, which is mandatory." % (GLOBAL_SECTION))
elif not ENTRY_POINT_KEY in conf[GLOBAL_SECTION]:
	raise SyntaxError("Missing mandatory '%s' key in '%s' section." % (ENTRY_POINT_KEY, GLOBAL_SECTION))
elif not conf[GLOBAL_SECTION][ENTRY_POINT_KEY] in conf:
	raise ValueError("Entry point '%s' not found." % (conf[GLOBAL_SECTION][ENTRY_POINT_KEY]))

entry_point = conf[GLOBAL_SECTION][ENTRY_POINT_KEY]
mem = []
section = conf[GLOBAL_SECTION][ENTRY_POINT_KEY]

while section:
	key_pressed = ""
	key_detected = False
	
	# SPEECH_KEY is mandatory
	if not conf[section][SPEECH_KEY]:
		raise ValueError("'%s' key is empty." % (SPEECH_KEY))
	print(conf[section][SPEECH_KEY])
	voc.play(conf[section][SPEECH_KEY])
	
	ts = time()
	while time()-ts<TIMEOUT:
		if key_detected:
			voc.stop()
			key_pressed = pi_dtmf.read()
			break
		if voc.is_playing():
			ts = time()
			sleep(0.1)
	
	
	if DEFAULT_KEY in conf[section] and not key_pressed:
		print("No key pressed, choosing default option.")
		key_pressed = DEFAULT_KEY
	elif key_pressed:
		print("Key pressed: %s" % (str(key_pressed)))
	
	if key_pressed:
		# Is the pressed key valid?
		if key_pressed in conf[section]:
			# If it is, get the matching value in config file
			v = conf[section][key_pressed]
			
			# First, is the value a known command?
			if v in ALLOWED_CMDS:
				if v == EXIT_CMD:
					print("Exit. Bye!")
					exit(0)
				elif v == MEMCLEAR_CMD:
					mem = []
					print("Memory cleared")
				elif v == RESET_CMD:
					mem = []
					section = entry_point
					print("Reset to the first section.")
			# If not, is it another section to play?
			elif v in conf:
				section = v
				print("Going to '%s' section." % (v))
			# Finally, if it isn't, just store it in memory
			else:
				print("Add '%s' to memory." % (v))
				mem.append(v)
		else:
			print("Invalid '%s' key pressed. Replay current section." % (key_pressed))
	else:
		print("No key was pressed. Replay current section.")
	key_pressed = ''
	#DBG
	print(mem)

exit(0)
