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

state = 0
press = 0
try:
	while 1:
		if state == 0:
			if GPIO.input(KEY_PRESS_PIN): # button is release
				if press == 1:
					#print("state 0 -> 1")
					press = 0
					state = 1
					serial = spi(device=0, port=0, bus_speed_hz = 8000000, transfer_size = 4096, gpio_DC = DC_PIN, gpio_RST = RST_PIN)
					device = sh1106(serial, rotate=2) #sh1106
					image = Image.new('1', (width, height))
					draw = ImageDraw.Draw(image)
					draw.rectangle((0,0,width,height), outline=0, fill=0)
			else: # button is pressed:
				press = 1

		if state == 1:
			with canvas(device) as draw:
				cmd = "hostname -I | cut -d\' \' -f1"
				IP = subprocess.check_output(cmd, shell = True )
				cmd = "top -bn1 | grep load | awk '{printf \"CPU Load: %.2f\", $(NF-2)}'"
				CPU = subprocess.check_output(cmd, shell = True )
				cmd = "free -m | awk 'NR==2{printf \"Mem: %s/%sMB %.2f%%\", $3,$2,$3*100/$2 }'"
				MemUsage = subprocess.check_output(cmd, shell = True )
				cmd = "df -h | awk '$NF==\"/\"{printf \"Disk: %d/%dGB %s\", $3,$2,$5}'"
				Disk = subprocess.check_output(cmd, shell = True )

				draw.text((xpos, top),       "IP: " + str(IP),  font=font, fill=255)
				draw.text((xpos, top+8),     str(CPU), font=font, fill=255)
				draw.text((xpos, top+16),    str(MemUsage),  font=font, fill=255)
				draw.text((xpos, top+25),    str(Disk),  font=font, fill=255)

				if GPIO.input(KEY_PRESS_PIN): # button is released
					if press == 1:
						#print("state 1 -> 0")
						GPIO.output(RST_PIN,GPIO.LOW)
						press = 0
						state = 0
				else: # button is pressed:
					press = 1
except:
	print("except")
GPIO.cleanup()