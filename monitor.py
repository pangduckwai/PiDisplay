# -*- coding:utf-8 -*-

from luma.core.interface.serial import i2c, spi
from luma.core.render import canvas
from luma.core import lib

from luma.oled.device import sh1106
import RPi.GPIO as GPIO

import time
import subprocess

from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont

#GPIO define
RST_PIN        = 25
CS_PIN         = 8
DC_PIN         = 24
KEY_UP_PIN     = 6 
KEY_DOWN_PIN   = 19
KEY_LEFT_PIN   = 5
KEY_RIGHT_PIN  = 26
KEY_PRESS_PIN  = 13
KEY1_PIN       = 21
KEY2_PIN       = 20
KEY3_PIN       = 16

#init GPIO
GPIO.setmode(GPIO.BCM) 
GPIO.setup(KEY_UP_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)    # Input with pull-up
GPIO.setup(KEY_DOWN_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)  # Input with pull-up
GPIO.setup(KEY_LEFT_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)  # Input with pull-up
GPIO.setup(KEY_RIGHT_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP) # Input with pull-up
GPIO.setup(KEY_PRESS_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP) # Input with pull-up
GPIO.setup(KEY1_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)      # Input with pull-up
GPIO.setup(KEY2_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)      # Input with pull-up
GPIO.setup(KEY3_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)      # Input with pull-up

font = ImageFont.load_default()
width = 128
height = 64

padding = -2
top = padding
bottom = height-padding
xpos = 0

SCREEN_SAVER = 30.0
press = 1
state = 0
start = time.time()
drawn = time.time()
try:
	while 1:
		stamp = time.time()
		if state == 0:
			if press == 1:
				press = 0
				state = 1
				start = time.time()

				# Initialize the display...
				serial = spi(device=0, port=0, bus_speed_hz = 8000000, transfer_size = 4096, gpio_DC = DC_PIN, gpio_RST = RST_PIN)
				device = sh1106(serial, rotate=2) #sh1106
				image = Image.new('1', (width, height))
				draw = ImageDraw.Draw(image)
				draw.rectangle((0,0,width,height), outline=0, fill=0)
			elif GPIO.input(KEY_PRESS_PIN) == 0:
				press = 1
			elif GPIO.input(KEY1_PIN) == 0:
				press = 1
			elif GPIO.input(KEY2_PIN) == 0:
				press = 1
			elif GPIO.input(KEY3_PIN) == 0:
				press = 1
			else:
				pass
		else: #state == 1
			if press == 1:
				GPIO.output(RST_PIN,GPIO.LOW)
				press = 0
				state = 0
			elif (GPIO.input(KEY_PRESS_PIN) == 0) or (GPIO.input(KEY1_PIN) == 0) or (GPIO.input(KEY2_PIN) == 0) or (GPIO.input(KEY3_PIN) == 0) or (stamp - start) > SCREEN_SAVER:
				press = 1 # Button pressed again, turning off display
			elif (stamp - drawn) > 1:
				drawn = stamp
				with canvas(device) as draw:
					DTTM = subprocess.check_output("date +\"%Y-%m-%d %H:%M:%S\"", shell = True)
					ADDR = subprocess.check_output("hostname -I | cut -d\' \' -f1", shell = True )
					CPUL = subprocess.check_output("top -bn1 | grep load | awk '{printf \"CPU : %.2f\", $(NF-2)}'", shell = True )
					MEMU = subprocess.check_output("free -m | awk 'NR==2{printf \"Mem : %s/%sMB %.2f%%\", $3,$2,$3*100/$2 }'", shell = True )
					DISK = subprocess.check_output("df -h | awk '$NF==\"/\"{printf \"Disk: %d/%dGB %s\", $3,$2,$5}'", shell = True )
					TEMP = subprocess.check_output("/opt/vc/bin/vcgencmd measure_temp | awk '{gsub(/temp=/,\" \"); print}'", shell = True )

					draw.text((xpos, top),    str(DTTM), font=font, fill=255)
					draw.text((xpos, top+12), "IP  : " + str(ADDR),  font=font, fill=255)
					draw.text((xpos, top+20), str(CPUL), font=font, fill=255)
					draw.text((xpos, top+28), str(MEMU),  font=font, fill=255)
					draw.text((xpos, top+36), str(DISK),  font=font, fill=255)
					draw.text((xpos, top+45), "Temp:" + str(TEMP), font=font, fill=255)
			else:
				pass

except:
	print("Stopped")
GPIO.cleanup()
