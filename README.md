# PiDisplay
Setup and use the Pi OLED HAT by Waveshare

128x64, 1.3inch OLED display HAT for Raspberry Pi

The **1.3" OLED Display HAT for [Raspberry Pi](https://www.raspberrypi.org/)** is a display HAT of the
same size of a [Pi Zero](https://www.raspberrypi.org/products/raspberry-pi-zero/). The information
provided by the manufacturer [Waveshare Electronics](https://www.waveshare.com/) is somewhat awkward,
I decided to document my journey here, along with the Python script I adopted to control the display.

## Hardware
The display attaches to a Pi Zero via the GPIO.  It is a 128 x 64 1.3" blue OLED display with a 5-ways
joystick on one side, and 3 buttons on the other:
* Driver: SH1106
* Interface: 4-wire SPI, 3-wire SPI, I2C
* Display color: blue
* Resolution: 128 x 64
* Operating voltage: 3.3V
The display has some jumpers at the back to be soldered to enable/disable the interfaces it uses.
I decided to use the default 4-wire SPI which require no soldering at all.

## Setup
I decided to use Python to control my display. There are other options from the manufacturer but I
didn't explore them.

_**Note: The following steps are deduced from the documents from the manufacturer. I performed them
in the exact order listed below, but I'm not sure if the ordering is necessary**_

### Prepare raspbian
* `sudo apt-get update`
* `sudo apt-get install python-dev`

### Install RPi.GPIO
* Download RPi.GPIO from [https://pypi.python.org/pypi/RPi.GPIO](https://pypi.python.org/pypi/RPi.GPIO) to somewhere.
* Extract the content (`tar xvfz RPi.GPIO-x.y.z.tar.gz`)
* `cd RPi.GPIO-x.y.z`
* `sudo python setup.py install`

### Install spidev
* Download spidev from [https://pypi.python.org/pypi/spidev](https://pypi.python.org/pypi/spidev) to somewhere.
* Extract the content (`tar xvfz spidev-x.y.tar.gz`)
* `sudo apt-get install python-smbus`
* `sudo apt-get install python-serial`
* `cd spidev-x.y`
* `sudo python setup.py install`

### Install Python Imaging
* `sudo apt-get install python-imaging`

### Enable the SPI interface
* `sudo raspi-config`
* Go to '5 Interfacing Options'
* Go to 'P4 SPI'
* Choose 'Yes'

### Enable the I2C interface
I'm not sure if this is necessary, but well what the hack...
* `sudo raspi-config`
* Go to '5 Interfacing Options'
* Go to 'P5 I2C'
* Choose 'Yes'

### Install the luma.oled driver
* `sudo apt-get install python-pip libfreetype6-dev libjpeg-dev`
* `sudo -H pip install --upgrade pip`
* `sudo apt-get purge python-pip`
* `sudo -H pip install --upgrade luma.oled`

## Test
That's it, the display is ready to use.

### Sample python app
* Download the sample apps from [https://www.waveshare.com/wiki/File:1.3inch-OLED-HAT-Code.7z](https://www.waveshare.com/wiki/File:1.3inch-OLED-HAT-Code.7z) to somewhere
* Extract the content somehow, I'm too lazy to find out how to handle 7z on Linux...
* `cd` to the subfolder containing the Python sample
* `sudo python demo.py`

## Next step
The Python code in this repo are adopted from `demo.py` by the manufacturer.