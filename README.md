# DTMF Server
A simple interactive voice response implementation. Designed to run
on a Raspberry Pi 2 (and later models) with the GPIO port, and a DTMF
module based on the MT8870 chip.

# Prerequisites
  - A Raspberry Pi 2 (or later model), with RaspiOS or another Linux
  operating system (see here how to install it:
  https://www.raspberrypi.org/documentation/installation/installing-images/README.md)
  - A DTMF module based on the MT8870 chip (like this:
  https://components101.com/modules/mt8870-dtmf-decoder-module)
  - Some wire, SIL connectors, resistors (see the following warning)
  and a soldering iron.

**Warning: be very carefull with the MT8870 module! The output voltage
is 5V, while the Raspberry Pi only expects 3.3V. Without conversion,
you'll DESTROY it, because there is no protection!**
  
You may find an example of a conversion scheme with some resistors here:
`voltage_conversion.png`

By default, Q1 to 4 outputs from MT8870 are respectively connected to
GPIO 1, 7, 8, 25 (in BCM pinout). StQ out is connected to GPIO 15,
and Inhibit input is wired to GPIO 14. You can change this behavior
in `pi_dtmf_reader.py` file.

# Installation
First, change audio output of the Raspberry Pi to the headphone jack,
with the `sudo raspi-config` command (see here for further instructions:
https://www.raspberrypi.org/documentation/configuration/audio-config.md).
Add the current user to the audio group: `sudo usermod -aG audio <my user>`.

Then, install TTS software SVoxPico. Since it is no longer in the official
RaspiOS repositories, you have to follow this custom install procedure:
https://davidjmurray.dev/pico-tts-engine-on-raspberry-pi/

Install the python3 dependancies: `sudo apt-get install python3-rpi.gpio
python3-pyaudio`.

And clone this repository. You're done!

# Usage
Using command line, go to the dtmf_server directory, and run
`./dtmf_server.py <your config file>`. The configuration file expected
by the program is the description of available menus and options. See
the next section for its syntax.

# Configuration file syntax

Work in progress...
