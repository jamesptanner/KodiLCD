# {"jsonrpc": "2.0", "method": "Player.PlayPause", "params": { "playerid": 0 }, "id": 1}
# {"jsonrpc": "2.0", "method": "Player.GoTo", "params": { "playerid": 0, "to": "next" }, "id": 1}
# {"jsonrpc": "2.0", "method": "Player.GoTo", "params": { "playerid": 0, "to": "previous" }, "id": 1}
# {"jsonrpc": "2.0", "method": "Player.GetActivePlayers", "id": 1}
# {"jsonrpc": "2.0", "method": "Player.GetItem", "params": { "properties": ["title", "album", "artist", "duration"], "playerid": 0 }, "id": "AudioGetItem"}
# {"jsonrpc": "2.0", "method": "Player.GetItem", "params": { "properties": ["title", "album", "artist", "season", "episode", "duration", "showtitle"], "playerid": 1 }, "id": "VideoGetItem"}
import httplib
import json
import time
import math
import threading

import Adafruit_CharLCD as LCD

lcd = LCD.Adafruit_CharLCDPlate()
lcd.set_color(1,0,0)

http = httplib.HttpConnection("192.168.1.143",8080)


def goToNext():
	lcd.clear()
	lcd.message("GOTO NEXT")

def goToPrev():
	lcd.clear()
	lcd.message("GOTO PREV")


def playPause():
	lcd.clear()
	lcd.message("PLAY/PAUSE")

def null_func():
	lcd.clear()
	lcd.message("NULL")

buttons = { LCD.SELECT : playPause,
           LCD.LEFT : goToPrev,
           LCD.UP : null_func,
           LCD.DOWN : null_func,
           LCD.RIGHT : goToNext }



#############################################################
def main():
	while True:
		for button in buttons.keys():
			if lcd.is_pressed(button):
				buttons[button]()
				while lcd.is_pressed(button):
					time.sleep(.5)

if __name__ == '__main__':
	main()
