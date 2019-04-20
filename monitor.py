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
RST_PIN  = 25
CS_PIN   = 8
DC_PIN   = 24
JS_U_PIN = 6 
JS_D_PIN = 19
JS_L_PIN = 5
JS_R_PIN = 26
JS_P_PIN = 13
BTN1_PIN = 21
BTN2_PIN = 20
BTN3_PIN = 16

#init GPIO
GPIO.setmode(GPIO.BCM) 
GPIO.setup(JS_U_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP) # Input with pull-up
GPIO.setup(JS_D_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP) # Input with pull-up
GPIO.setup(JS_L_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP) # Input with pull-up
GPIO.setup(JS_R_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP) # Input with pull-up
GPIO.setup(JS_P_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP) # Input with pull-up
GPIO.setup(BTN1_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP) # Input with pull-up
GPIO.setup(BTN2_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP) # Input with pull-up
GPIO.setup(BTN3_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP) # Input with pull-up

font = ImageFont.load_default()
width = 128
height = 64

padding = -2
top = padding
bottom = height-padding
xpos = 0

SCREEN_SAVER = 20.0

GPIO.add_event_detect(JS_P_PIN, GPIO.RISING)
GPIO.add_event_detect(BTN1_PIN, GPIO.RISING)
GPIO.add_event_detect(BTN2_PIN, GPIO.RISING)
GPIO.add_event_detect(BTN3_PIN, GPIO.RISING)

press = 1
state = 0
start = time.time()
try:
	while True:
		stamp = time.time()

		if GPIO.event_detected(JS_P_PIN):
			press = 1

		if GPIO.event_detected(BTN1_PIN):
			press = 2

		if GPIO.event_detected(BTN2_PIN):
			press = 4

		if GPIO.event_detected(BTN3_PIN):
			press = 8

		if state == 0: # Display is off
			if press > 0:
				press = 0
				state = 1
				start = time.time()

				# Initialize the display...
				serial = spi(device=0, port=0, bus_speed_hz = 8000000, transfer_size = 4096, gpio_DC = DC_PIN, gpio_RST = RST_PIN)
				device = sh1106(serial, rotate=2) #sh1106
				image = Image.new('1', (width, height))
				draw = ImageDraw.Draw(image)
				draw.rectangle((0,0,width,height), outline=0, fill=0)
			else:
				pass
		elif state == 1:
			if (press > 0) or ((stamp - start) > SCREEN_SAVER): # Signal to turn off display
				GPIO.output(RST_PIN,GPIO.LOW)
				press = 0
				state = 0
			else:
				pass

			with canvas(device) as draw:
				DTTM = subprocess.check_output("date +\"%Y-%m-%d %H:%M:%S\"", shell = True)
				ADDR = subprocess.check_output("hostname -I | cut -d\' \' -f1", shell = True )
				CPUL = subprocess.check_output("top -bn1 | awk 'NR==3{printf \"CPU : %.1f%% idle\", $8}'", shell = True )
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

		time.sleep(1)

except:
	print "Stopped"
GPIO.cleanup()
