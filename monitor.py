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
x0 = 0
x1 = 70
y0 = -2
y1 = 12
# ypos2 = 24
# ypos3 = 36
# ypos4 = 48

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
horz = 0 #Selection choice: 0 - Left; 1 - Right
vert = 4 #Selection choice: 1 - Top; 2 - Second; 3 - Third; 4 - Bottom
stamp = time.time() #Current timestamp
start = time.time() #Start screen saver count down

def take_act(channel):
	global start
	global vert
	if state == BTN3_PIN:
		if vert == 1:
			draw_scn(RST_PIN)
			os.system("sudo shutdown -h now")
		elif vert == 2:
			# Remount
			draw_scn(997)
			start = stamp - SCREEN_SAVER - 10
			os.system("sudo /usr/bin/usb_drive.sh remount")
		elif vert == 3:
			# Replug USB
			draw_scn(998)
			start = stamp - SCREEN_SAVER - 10
			os.system("sudo /usr/bin/usb_drive.sh replug")
		else:
			show_stt(BTN1_PIN)
	else:
		vert = 4 # Default
		show_stt(BTN3_PIN)

def select_h(channel):
	global start
	global horz
	if channel == JS_L_PIN:
		start = time.time()
		horz = 1
		draw_scn(state)
	elif channel == JS_R_PIN:
		start = time.time()
		horz = 0
		draw_scn(state)
	else:
		pass

def select_v(channel):
	global start
	global vert
	if channel == JS_U_PIN:
		start = time.time()
		if vert > 1:
			vert = vert - 1
	elif channel == JS_D_PIN:
		start = time.time()
		if vert < 4:
			vert = vert + 1
	else:
		pass

def draw_scn(channel):
	with canvas(device) as draw:
		LINE0 = subprocess.check_output("date +\"%Y-%m-%d %H:%M:%S\"", shell = True)
		LINE1 = ""
		LINE2 = ""
		LINE3 = ""
		LINE4 = ""
		if channel == BTN1_PIN:
			if horz == 0:
				ssid = subprocess.check_output("iwgetid --raw | awk '{printf \"WiFi:%s\", $0}'", shell = True)
				freq = subprocess.check_output("iwgetid --freq | awk '{gsub(/Frequency:/,\"\"); printf \" %.1f %s\", $2,$3}'", shell = True)
				LINE1 = subprocess.check_output("df -h /mnt/usb | awk '$NF==\"/mnt/usb\"{printf \"Disk:%s/%s %s\", $3,$2,$5}'", shell = True )
				LINE2 = ssid + freq
				LINE3 = "  in Kbps  out Kbps"
				LINE4 = subprocess.check_output("ifstat -bT 0.1 1 | awk 'NR==3{printf \"%9.2f %9.2f\",$3,$4}'", shell = True)
				draw.rectangle((19,61,48,63), outline=255, fill=0)
				draw.rectangle((49,61,109,63), outline=255, fill=1)
			else:
				LINE1 = subprocess.check_output("hostname -I | awk '{printf \"IP :%s\", $1}'", shell = True )
				LINE2 = subprocess.check_output("top -bn1 | awk 'NR==3{printf \"CPU:%.1f%% idle\", $8}'", shell = True )
				LINE3 = subprocess.check_output("free -mh | awk 'NR==2{printf \"Mem:%s/%s %.1f%%\", $3,$2,$3*100/$2 }'", shell = True )
				LINE4 = subprocess.check_output("cat /sys/class/thermal/thermal_zone0/temp | awk '{printf \"Tmp:%.1fC\", $1/1000}'", shell = True )
				draw.rectangle((19,61,78,63), outline=255, fill=1)
				draw.rectangle((79,61,109,63), outline=255, fill=0)
		elif channel == BTN3_PIN:
			LINE1 = "> Shutdown"
			LINE2 = "> Reset SMB"
			LINE3 = "> Reset USB"
			LINE4 = "> Cancel"
			draw.polygon([(x1,y1*vert+6),(x1+7,y1*vert-1),(x1+7,y1*vert+4),(x1+14,y1*vert+4),(x1+14,y1*vert+8),(x1+7,y1*vert+8),(x1+7,y1*vert+13)], outline=255, fill=1)
		elif channel == RST_PIN:
			LINE2 = " Shutting down..."
		elif channel == 997:
			LINE2 = " Resetting SMB..."
		elif channel == 998:
			LINE2 = " Resetting USB..."
		else:
			pass

		draw.text((x0, y0),    LINE0, font=font, fill=255)
		if len(LINE1) > CHAR_WIDTH:
			draw.text((x0, y1), LINE1[:CHAR_WIDTH], font=font, fill=255)
		else:
			draw.text((x0, y1), LINE1, font=font, fill=255)

		if len(LINE2) > CHAR_WIDTH:
			draw.text((x0, y1*2), LINE2[:CHAR_WIDTH], font=font, fill=255)
		else:
			draw.text((x0, y1*2), LINE2, font=font, fill=255)

		if len(LINE3) > CHAR_WIDTH:
			draw.text((x0, y1*3), LINE3[:CHAR_WIDTH], font=font, fill=255)
		else:
			draw.text((x0, y1*3), LINE3, font=font, fill=255)

		if len(LINE4) > CHAR_WIDTH:
			draw.text((x0, y1*4), LINE4[:CHAR_WIDTH], font=font, fill=255)
		else:
			draw.text((x0, y1*4), LINE4, font=font, fill=255)

def show_stt(channel):
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
			draw_scn(channel)
		else:
			pass
	else: # Display is on
		if ((channel > 0) and (channel == state)) or ((stamp - start) > SCREEN_SAVER): # A button is pressed or timed out, turn off display
			GPIO.output(RST_PIN,GPIO.LOW)
			state = 0
		elif (channel > 0) and (channel != state):
			state = channel
			start = time.time()
			draw_scn(channel)
		else: # state > 0 && channel == 0 && not-yet-timeout, refresh screen
			draw_scn(state)

GPIO.add_event_detect(BTN1_PIN, GPIO.RISING, callback=show_stt, bouncetime=200)
GPIO.add_event_detect(BTN3_PIN, GPIO.RISING, callback=take_act, bouncetime=200)
GPIO.add_event_detect(JS_L_PIN, GPIO.RISING, callback=select_h, bouncetime=200)
GPIO.add_event_detect(JS_R_PIN, GPIO.RISING, callback=select_h, bouncetime=200)
GPIO.add_event_detect(JS_U_PIN, GPIO.RISING, callback=select_v, bouncetime=200)
GPIO.add_event_detect(JS_D_PIN, GPIO.RISING, callback=select_v, bouncetime=200)

# Main Loop
try:
	show_stt(BTN1_PIN)
	while True:
		stamp = time.time()
		show_stt(0)
		time.sleep(1)

except:
	print "Stopped", sys.exc_info()[0]
	raise
GPIO.cleanup()
