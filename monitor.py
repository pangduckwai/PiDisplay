# -*- coding:utf-8 -*-

from luma.core.interface.serial import i2c, spi
from luma.core.render import canvas
from luma.core import lib

from luma.oled.device import sh1106
import RPi.GPIO as GPIO

import sys
import time
import subprocess
import os

from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont

#GPIO define
RST_PIN  = 25 #Reset
CS_PIN   = 8
DC_PIN   = 24
JS_U_PIN = 6  #Joystick Up
JS_D_PIN = 19 #Joystick Down
JS_L_PIN = 5  #Joystick Left
JS_R_PIN = 26 #Joystick Right
JS_P_PIN = 13 #Joystick Pressed
BTN1_PIN = 21
BTN2_PIN = 20
BTN3_PIN = 16

# Some constants
SCREEN_SAVER = 20.0
CHAR_WIDTH = 19
font = ImageFont.load_default()
width = 128
height = 64
padding = -2
top = padding
bottom = height-padding
xpos = 0

# init GPIO
GPIO.setmode(GPIO.BCM) 
GPIO.setup(JS_U_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP) # Input with pull-up
GPIO.setup(JS_D_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP) # Input with pull-up
GPIO.setup(JS_L_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP) # Input with pull-up
GPIO.setup(JS_R_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP) # Input with pull-up
GPIO.setup(JS_P_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP) # Input with pull-up
GPIO.setup(BTN1_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP) # Input with pull-up
GPIO.setup(BTN2_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP) # Input with pull-up
GPIO.setup(BTN3_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP) # Input with pull-up

# Initialize the display...
serial = spi(device=0, port=0, bus_speed_hz = 8000000, transfer_size = 4096, gpio_DC = DC_PIN, gpio_RST = RST_PIN)
device = sh1106(serial, rotate=2) #sh1106
draw = ImageDraw.Draw(Image.new('1', (width, height)))
draw.rectangle((0,0,width,height), outline=0, fill=0)

state = 0 #System state: 0 - scrren is off; equal to channel number (e.g. BTN2_PIN, JS_P_PIN) otherwise
stops = 0 #Shutdown choice: 0 - No; 1 - Yes
stamp = time.time() #Current timestamp
start = time.time() #Start screen saver count down

def shutdown(channel):
	global stops
	if state == BTN3_PIN:
		if stops == 1:
			draw_process(RST_PIN)
			os.system("sudo shutdown -h now")
		else:
			main_process(BTN1_PIN)
	else:
		stops = 0
		main_process(BTN3_PIN)

def select(channel):
	global stops
	if state == BTN3_PIN:
		if channel == JS_L_PIN:
			stops = 1
			draw_process(state)
		elif channel == JS_R_PIN:
			stops = 0
			draw_process(state)
		else:
			pass

def draw_process(channel):
	with canvas(device) as draw:
		LINE0 = subprocess.check_output("date +\"%Y-%m-%d %H:%M:%S\"", shell = True)
		LINE1 = ""
		LINE2 = ""
		LINE3 = ""
		LINE4 = ""
		if channel == BTN2_PIN:
			LINE1 = subprocess.check_output("hostname -I | awk '{printf \"IP :%s\", $1}'", shell = True )
			LINE2 = subprocess.check_output("top -bn1 | awk 'NR==3{printf \"CPU:%.1f%% idle\", $8}'", shell = True )
			LINE3 = subprocess.check_output("free -mh | awk 'NR==2{printf \"Mem:%s/%s %.1f%%\", $3,$2,$3*100/$2 }'", shell = True )
			LINE4 = subprocess.check_output("cat /sys/class/thermal/thermal_zone0/temp | awk '{printf \"Tmp:%.1fC\", $1/1000}'", shell = True )
		elif channel == BTN1_PIN:
			ssid = subprocess.check_output("iwgetid --raw | awk '{printf \"WiFi:%s\", $0}'", shell = True)
			freq = subprocess.check_output("iwgetid --freq | awk '{gsub(/Frequency:/,\"\"); printf \" %.1f %s\", $2,$3}'", shell = True)
			LINE1 = subprocess.check_output("df -h /mnt/usb | awk '$NF==\"/mnt/usb\"{printf \"Disk:%s/%s %s\", $3,$2,$5}'", shell = True )
			LINE2 = ssid + freq
			LINE3 = "  in Kbps  out Kbps"
			LINE4 = subprocess.check_output("ifstat -bT 0.1 1 | awk 'NR==3{printf \"%9.2f %9.2f\",$3,$4}'", shell = True)
		elif channel == BTN3_PIN:
			LINE1 = "    Shutdown ?"
			LINE3 = "   Yes       No"
			if stops == 0:
				draw.rectangle((72,50,94,52), outline=255, fill=1)
			else:
				draw.rectangle((15,50,37,52), outline=255, fill=1)
		elif channel == RST_PIN:
			LINE2 = " Shutting down..."
		else:
			pass

		draw.text((xpos, top),    LINE0, font=font, fill=255)
		if len(LINE1) > CHAR_WIDTH:
			draw.text((xpos, top+12), LINE1[:CHAR_WIDTH], font=font, fill=255)
		else:
			draw.text((xpos, top+12), LINE1, font=font, fill=255)

		if len(LINE2) > CHAR_WIDTH:
			draw.text((xpos, top+28), LINE2[:CHAR_WIDTH], font=font, fill=255)
		else:
			draw.text((xpos, top+28), LINE2, font=font, fill=255)

		if len(LINE3) > CHAR_WIDTH:
			draw.text((xpos, top+40), LINE3[:CHAR_WIDTH], font=font, fill=255)
		else:
			draw.text((xpos, top+40), LINE3, font=font, fill=255)

		if len(LINE4) > CHAR_WIDTH:
			draw.text((xpos, top+52), LINE4[:CHAR_WIDTH], font=font, fill=255)
		else:
			draw.text((xpos, top+52), LINE4, font=font, fill=255)

def main_process(channel):
	global serial
	global device
	global draw
	global state
	global start
	if state <= 0: # Display is off
		if channel > 0: # A button is pressed, turn on display
			# Initialize the display...
			serial = spi(device=0, port=0, bus_speed_hz = 8000000, transfer_size = 4096, gpio_DC = DC_PIN, gpio_RST = RST_PIN)
			device = sh1106(serial, rotate=2) #sh1106
			image = Image.new('1', (width, height))
			draw = ImageDraw.Draw(image)
			draw.rectangle((0,0,width,height), outline=0, fill=0)

			state = channel
			start = time.time()
			draw_process(channel)
		else:
			pass
	else: # Display is on
		if ((channel > 0) and (channel == state)) or ((stamp - start) > SCREEN_SAVER): # A button is pressed or timed out, turn off display
			GPIO.output(RST_PIN,GPIO.LOW)
			state = 0
		elif (channel > 0) and (channel != state):
			state = channel
			start = time.time()
			draw_process(channel)
		else: # state > 0 && channel == 0 && not-yet-timeout, refresh screen
			draw_process(state)

GPIO.add_event_detect(BTN1_PIN, GPIO.RISING, callback=main_process, bouncetime=200)
GPIO.add_event_detect(BTN2_PIN, GPIO.RISING, callback=main_process, bouncetime=200)
GPIO.add_event_detect(BTN3_PIN, GPIO.RISING, callback=shutdown, bouncetime=200)
GPIO.add_event_detect(JS_L_PIN, GPIO.RISING, callback=select, bouncetime=200)
GPIO.add_event_detect(JS_R_PIN, GPIO.RISING, callback=select, bouncetime=200)


try:
	main_process(BTN1_PIN)
	while True:
		stamp = time.time()
		main_process(0)
		time.sleep(1)

except:
	print "Stopped", sys.exc_info()[0]
	raise
GPIO.cleanup()
