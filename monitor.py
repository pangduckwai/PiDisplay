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
import string

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
SCREEN_LINES = 4
SCREEN_SAVER = 20.0
CHAR_WIDTH = 19
font = ImageFont.load_default()
width = 128
height = 64
x0 = 0
x1 = 84
y0 = -2
y1 = 12
x2 = x1+7
x3 = x1+14
x4 = x1+9
x5 = x2+9
x6 = x3+9

choices = [
	["a","b","c","d","e","f","g","h","i","j","k","l","m","n","o","p","q","r","s","t","u","v","w","x","y","z"],
	["A","B","C","D","E","F","G","H","I","J","K","L","M","N","O","P","Q","R","S","T","U","V","W","X","Y","Z"],
	["0","1","2","3","4","5","6","7","8","9","!","@","#","$","%","^","&","*","(",")",",",".","?",":",";","'"]
]

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
horz = 1 #Selection choice: 0 - Right; 1 - Left
vert = 3 #Selection choice: 1 - Top; 2 - Middle; 3 - Bottom
stamp = time.time() #Current timestamp
start = time.time() #Start screen saver count down
iface = ""
idxWin = 0
idxLen = 0
aplist = []
apIndx = -1
pwdLst = []
pwdLen = 0
chaSel = 1 #possible values: 0, 1, 2

test = 0 # For testing!@1!!!!!!!!!!!!!!!!!!!!

def click_b1(channel):
	global chaSel
	if state == BTN1_PIN:
		main_fun(channel)
	else:
		if apIndx < 0:
			main_fun(BTN1_PIN)
		else:
			if chaSel > 0:
				chaSel = chaSel - 1
				pwdLst[horz] = choices[chaSel][vert]
				main_fun(BTN2_PIN)

def click_b3(channel):
	global start
	global vert
	global apIndx
	global chaSel
	if state == BTN3_PIN:
		apIndx = -1
		if vert == 1:
			if horz == 1:
				main_fun(995)
				os.system("sudo shutdown -h now")
			else:
				main_fun(996)
				os.system("sudo shutdown -r now")
		elif vert == 2:
			main_fun(997)
			os.system("sudo usb_drive.sh refresh")
			start = stamp - SCREEN_SAVER + 5
		else:
			main_fun(BTN1_PIN)
	else:
		if apIndx < 0:
			vert = 3 # Default
			main_fun(BTN3_PIN)
		else:
			if chaSel < 2:
				chaSel = chaSel + 1
				pwdLst[horz] = choices[chaSel][vert]
				main_fun(BTN2_PIN)

def click_b2(channel):
	global aplist
	global idxWin
	global idxLen
	global start
	global vert
	global test

	start = time.time()

	if apIndx >= 0:
		main_fun(998)
		print ''.join(pwdLst) #TODO change password for real...
		start = stamp - SCREEN_SAVER + 5
	else:
		result = os.popen("iwlist {0} scan 2>/dev/null | grep '^..*ESSID:\"..*\"$' | sed 's/^.*ESSID:\"\\(..*\\)\".*$/\\1/'".format(iface)).read()
		aplist = result.splitlines()

		idxLen = len(aplist)
		if (idxWin + SCREEN_LINES) > idxLen:
			idxWin = idxLen - SCREEN_LINES
			if idxWin < 0:
				idxWin = 0

		if vert > idxLen:
			vert = idxLen

		main_fun(channel)

def select_h(channel):
	global apIndx
	global start
	global pwdLen
	global horz
	global vert
	if state == BTN2_PIN:
		if apIndx < 0: #select ssid mode
			if channel == JS_L_PIN or channel == JS_R_PIN:
				start = time.time()
				apIndx = idxWin + vert - 1
				pwdLen = len(pwdLst)
				if (pwdLen > 0):
					horz = pwdLen - 1
				else:
					horz = 0
		else: #input mode
			if channel == JS_L_PIN:
				start = time.time()
				if horz > 0:
					horz = horz - 1
				else:
					apIndx = -1 #Exit input mode
					horz = 0
					vert = 1
			elif channel == JS_R_PIN:
				start = time.time()
				if horz < pwdLen:
					horz = horz + 1
	else:
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
	global idxWin
	global start
	global vert
	if state == BTN2_PIN:
		if apIndx < 0: #select ssid mode
			if channel == JS_U_PIN:
				start = time.time()
				if vert > 1:
					vert = vert - 1
				elif idxWin > 0:
					idxWin = idxWin - 1
			elif channel == JS_D_PIN:
				start = time.time()
				if vert < 4 and vert < idxLen:
					vert = vert + 1
				elif (idxWin + SCREEN_LINES) < idxLen:
					idxWin = idxWin + 1
			else:
				pass
		else: #input mode
			if channel == JS_U_PIN:
				start = time.time()
				if vert > 0:
					vert = vert - 1
				else:
					vert = 25
			elif channel == JS_D_PIN:
				start = time.time()
				if vert < 25:
					vert = vert + 1
				else:
					vert = 0
			pwdLst[horz] = choices[chaSel][vert]
	else:
		if vert > 3:
			vert = 3
		if channel == JS_U_PIN:
			start = time.time()
			if vert > 1:
				vert = vert - 1
		elif channel == JS_D_PIN:
			start = time.time()
			if vert < 3:
				vert = vert + 1
		else:
			pass

def draw_scn(channel):
	global idxLen
	global pwdLen
	global apIndx
	with canvas(device) as draw:
		LINE0 = subprocess.check_output("date +\"%Y-%m-%d %H:%M:%S\"", shell = True)
		LINE1 = ""
		LINE2 = ""
		LINE3 = ""
		LINE4 = ""
		if channel == BTN1_PIN:
			if horz == 1:
				ssid = subprocess.check_output("iwgetid --raw | awk '{printf \"WiFi:%s\", $0}'", shell = True)
				freq = subprocess.check_output("iwgetid --freq | awk '{gsub(/Frequency:/,\"\"); printf \" %.1f %s\", $2,$3}'", shell = True)
				LINE1 = subprocess.check_output("hostname -I | awk '{printf \"IP: %s\", $1}'", shell = True )
				LINE2 = subprocess.check_output("df -h /mnt/usb | awk '$NF==\"/mnt/usb\"{printf \"Disk:%s/%s %s\", $3,$2,$5}'", shell = True )
				LINE3 = ssid + freq
				LINE4 = subprocess.check_output("cat /sys/class/thermal/thermal_zone0/temp | awk '{printf \"Temp:%.1fC\", $1/1000}'", shell = True )
				draw.rectangle((0,61,84,63), outline=255, fill=1)
				draw.rectangle((85,61,127,63), outline=255, fill=0)
			else:
				LINE1 = subprocess.check_output("top -bn1 | awk 'NR==3{printf \"CPU:%.1f%% idle\", $8}'", shell = True )
				LINE2 = subprocess.check_output("free -mh | awk 'NR==2{printf \"Mem:%s/%s %.1f%%\", $3,$2,$3*100/$2 }'", shell = True )
				LINE3 = "  in Kbps  out Kbps"
				LINE4 = subprocess.check_output("ifstat -bT 0.1 1 | awk 'NR==3{printf \"%9.2f %9.2f\",$3,$4}'", shell = True)
				draw.rectangle((0,61,42,63), outline=255, fill=0)
				draw.rectangle((43,61,127,63), outline=255, fill=1)
		elif channel == BTN3_PIN:
			y2 = y1*vert
			LINE1 = "| Shutdown..."
			LINE2 = "| Refresh"
			LINE3 = "| Cancel"

			if vert == 1:
				if horz == 1:
					LINE1 = "> Shutdown"
				else:
					LINE1 = "> Reboot"
			elif vert == 2:
				LINE2 = "> Refresh"
			else:
				LINE3 = "> Cancel"

			if vert == 1:
				if horz == 1:
					draw.polygon([(x4,y2+6),(x5,y2-1),(x5,y2+4),(x6,y2+4),(x6,y2+8),(x5,y2+8),(x5,y2+13)], outline=255, fill=0)
					draw.polygon([(x1,y2+6),(x2,y2-1),(x2,y2+4),(x3,y2+4),(x3,y2+8),(x2,y2+8),(x2,y2+13)], outline=255, fill=1)
				else:
					draw.polygon([(x1,y2+6),(x2,y2-1),(x2,y2+4),(x3,y2+4),(x3,y2+8),(x2,y2+8),(x2,y2+13)], outline=255, fill=0)
					draw.polygon([(x4,y2+6),(x5,y2-1),(x5,y2+4),(x6,y2+4),(x6,y2+8),(x5,y2+8),(x5,y2+13)], outline=255, fill=1)
			else:
				draw.polygon([(x1,y2+6),(x2,y2-1),(x2,y2+4),(x3,y2+4),(x3,y2+8),(x2,y2+8),(x2,y2+13)], outline=255, fill=1)

		elif channel == BTN2_PIN:
			if apIndx < 0: #select ssid mode
				y2 = y1*vert
				if (idxWin >= 0) and (idxWin < idxLen):
					LINE1 = aplist[idxWin]
				if (idxWin + 1 < idxLen):
					LINE2 = aplist[idxWin + 1]
				if (idxWin + 2 < idxLen):
					LINE3 = aplist[idxWin + 2]
				if (idxWin + 3 < idxLen):
					LINE4 = aplist[idxWin + 3]

				draw.polygon([(x1,y2+6),(x2,y2-1),(x2,y2+4),(x3,y2+4),(x3,y2+8),(x2,y2+8),(x2,y2+13)], outline=255, fill=1)
				draw.rectangle((125,12,127,60), outline=255, fill=0)

				thumb_s = 48.0 / idxLen #Step
				thumb_h = thumb_s * 4 #Because the screen can display 4 rows at a time
				thumb_0 = idxWin * thumb_s + 12
				thumb_1 = thumb_0 + thumb_h
				if thumb_1 > 60:
					thumb_1 = 60
				draw.rectangle((125, thumb_0, 127, thumb_1), outline=255, fill=1)
			else: #input mode
				if horz >= pwdLen:
					pwdLst.append(choices[chaSel][vert])
					pwdLen = len(pwdLst)

				cursorx = 6 * horz
				cursory = y1 * 2
				draw.text((122, y1)  , choices[0][vert], font=font, fill=255)
				draw.text((122, y1*2), choices[1][vert], font=font, fill=255)
				draw.text((122, y1*3), choices[2][vert], font=font, fill=255)
				draw.rectangle((cursorx,cursory+10,cursorx+4,cursory+11), outline=255, fill=1)

				LINE1 = "SSID: " + aplist[apIndx]
				if pwdLen > 0:
					LINE2 = ''.join(pwdLst)

		elif channel == 995:
			LINE2 = " Shutting down..."
		elif channel == 996:
			LINE2 = " Rebooting..."
		elif channel == 997:
			LINE2 = " Refreshing..."
		elif channel == 998:
			LINE1 = "Setting passphrase"
			LINE2 = "of '" + aplist[apIndx] + "'"
		else:
			pass

		draw.text((x0, y0), LINE0, font=font, fill=255)
		if len(LINE1) > CHAR_WIDTH:
			draw.text((x0, y1),   LINE1[:CHAR_WIDTH], font=font, fill=255)
		else:
			draw.text((x0, y1),   LINE1, font=font, fill=255)

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

def main_fun(channel):
	global serial
	global device
	global draw
	global state
	global start
	global apIndx
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
			apIndx = -1
			draw_scn(channel)
		else:
			pass
	else: # Display is on
		if ((channel > 0) and (channel == state) and ((channel != BTN2_PIN) or (apIndx < 0))) or ((stamp - start) > SCREEN_SAVER): # A button is pressed or timed out, turn off display
			GPIO.output(RST_PIN,GPIO.LOW)
			state = 0
			apIndx = -1
		elif (channel > 0) and (channel != state) and ((state != BTN2_PIN) or (apIndx < 0) or (channel == 998)):
			state = channel
			start = time.time()
			draw_scn(channel)
		else: # state > 0 && channel == 0 && not-yet-timeout, refresh screen
			draw_scn(state)

GPIO.add_event_detect(BTN1_PIN, GPIO.RISING, callback=click_b1, bouncetime=200)
GPIO.add_event_detect(BTN2_PIN, GPIO.RISING, callback=click_b2, bouncetime=200)
GPIO.add_event_detect(BTN3_PIN, GPIO.RISING, callback=click_b3, bouncetime=200)
GPIO.add_event_detect(JS_L_PIN, GPIO.RISING, callback=select_h, bouncetime=200)
GPIO.add_event_detect(JS_R_PIN, GPIO.RISING, callback=select_h, bouncetime=200)
GPIO.add_event_detect(JS_U_PIN, GPIO.RISING, callback=select_v, bouncetime=200)
GPIO.add_event_detect(JS_D_PIN, GPIO.RISING, callback=select_v, bouncetime=200)

iface = subprocess.check_output("iwgetid | awk '{print $1}'", shell = True).rstrip("\r\n")

# Main Loop
try:
	main_fun(BTN1_PIN)
	while True:
		stamp = time.time()
		main_fun(0)
		time.sleep(1)

except:
	print "Stopped", sys.exc_info()[0]
	raise
GPIO.cleanup()