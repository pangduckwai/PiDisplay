# PiDisplay
Setup and use the 1.3" OLED Display HAT for Raspberry Pi by Waveshare

The **[1.3" OLED Display HAT for Raspberry Pi](https://www.waveshare.com/product/modules/oleds-lcds/oled/1.3inch-oled-hat.htm)** is a display the
same size of a [Raspberry Pi Zero](https://www.raspberrypi.org/products/raspberry-pi-zero/). The information
provided by the manufacturer [Waveshare Electronics](https://www.waveshare.com/) is somewhat awkward,
so I decided to document my journey here, along with the Python script I adopted to control the display.

## Hardware
The display attaches to a Pi via the GPIO.  It is a 128x64 1.3" blue OLED display with a 5-way
joystick on one side, and 3 buttons on the other:
* Driver: SH1106
* Interface: 4-wire SPI, 3-wire SPI, I2C
* Operating voltage: 3.3V

The display has some jumpers at the back to be soldered to enable/disable the interfaces it uses.
It is a no-brainer to use the default 4-wire SPI which require no soldering at all.

##Raspberry Pi OS Version
I got some problems with newer versions of raspbian with this screen probably because of the kernel version packages not compatible with the ones this screen needs to make a proper connetion so I'm using this one, it's the last version of the 4.9:
https://downloads.raspberrypi.org/raspbian/images/raspbian-2019-04-09/

## Setup
I decided to use Python to control my display. There are other options from the manufacturer but I
haven't explore them.

_**Note: The following steps are deduced from the documents provided by the manufacturer. I performed them
in the exact order listed below, but I'm not sure if that is absolutely necessary...**_

### Prepare raspbian
Install the following packages:
* `sudo apt-get update`
* `sudo apt-get install python3-dev python3-pip libffi-dev libssl-dev`
* `sudo pip3 install --upgrade pip`
* `sudo apt-get purge python3-pip`
* `sudo pip3 install --upgrade luma.oled`
* `sudo pip3 install smbus`
* `sudo apt-get install python3-numpy`
* `sudo apt-get install libopenjp2-7`
* `sudo apt install libtiff5`
* `sudo apt-get install ifstat`

### Enable the SPI interface
* `sudo raspi-config`
* Go to '5 Interfacing Options'
* Go to 'P4 SPI'
* Choose 'Yes'

### Enable the I2C interface
Not sure if this is necessary, but well what the hack...
* `sudo raspi-config`
* Go to '5 Interfacing Options'
* Go to 'P5 I2C'
* Choose 'Yes'

## Fork
I rearanged the position of the Information lines.
The first page is harware only and instead of displaying the Ip I added a SD card space left
The next page is all network, the ip + ssid and network transfer speeds


## Next step
The Python code in this repo (`monitor.py`) display system information of the Pi:
1. **Button 1** - Display system information of the Pi, such as _Disk space_, _WiFi status_, _IP Address_, _CPU Idle %_, _Memory usage_, _Network status_ and _System temperature_, in 2 pages; use the Left/Right Joystick to toggle between these pages.
1. **Button 3** - Display the system action dialog, use the Up/Down/Left/Right Joystick to select the options between _Reboot_, _Shutdown_, _Re-mount Samba_ and _Reload the USB driver_. Press **Button 3** to confirm your choice.
* The screen will turn off after idling for around 20 seconds.
* The shell script (`usb_drive.sh`) referenced in the Python code is also included in this repo.

### CPU usage
The original version was adopted directly from `demo.py` provided by the manufacturer, which is no good for 'production' use. Because your Pi will be too busy looking for button inputs instead of doing anything else useful.

The latest version utilize GPIO input detection instead of busy wait, which is much more reasonable CPU-wise.

### Enable the display at startup
* `sudo vi /etc/rc.local`
  * Add the following line JUST ABOVE exit 0, assuming `monitor.py` is in /home/pi/:
  * `python /home/pi/monitor.py &`
  * _**IMPORTANT**_ Don't forget the `&` character at the end!