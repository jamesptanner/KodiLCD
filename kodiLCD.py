# {"jsonrpc": "2.0", "method": "Player.GetItem", "params": { "properties": ["title", "album", "artist", "duration"], "playerid": 0 }, "id": "AudioGetItem"}
# {"jsonrpc": "2.0", "method": "Player.GetItem", "params": { "properties": ["title", "album", "artist", "season", "episode", "duration", "showtitle"], "playerid": 1 }, "id": "VideoGetItem"}
import httplib, urllib
import json
import time
import math
import threading

import Adafruit_CharLCD as LCD

lcd = LCD.Adafruit_CharLCDPlate()
http = httplib.HTTPConnection("192.168.1.143",8080)

screenOffline = True

MODE_NONE = 0
MODE_VIDEO = 1
MODE_AUDIO = 2

class NowPlayingThread(threading.Thread):
	def __init__(self):
		super(NowPlayingThread,self).__init__()
		self.item={}
		self.mode=MODE_NONE
	def setMode(mode):
		if MODE_NONE <= mode <= MODE_AUDIO:
			self.mode = mode
	def run(self):
		pass
	
def postKodiCommand(postCmd):
	print postCmd
	postHeader = {'Content-Type':'application/json'}
	http.request("POST", "/jsonrpc",postCmd,postHeader)
	response = http.getresponse()
	print response.status, response.reason
	jsonResponse = response.read()
	print jsonResponse
	return json.loads(jsonResponse)

def getActivePlayer():
	# {"jsonrpc": "2.0", "method": "Player.GetActivePlayers", "id": 1}
	# {"id":1,"jsonrpc":"2.0","result":[{"playerid":1,"type":"video"}]}
	# {"id":1,"jsonrpc":"2.0","result":[]}
	postCmd = '''{"jsonrpc": "2.0", "method": "Player.GetActivePlayers", "id": 1}'''
	resp = postKodiCommand(postCmd)
	players = resp['result']
	if len(players)==0:
		return None
	else:
		return players[0]

def goToNext():
	# {"jsonrpc": "2.0", "method": "Player.GoTo", "params": { "playerid": 0, "to": "next" }, "id": 1}
	postCmd = '{"jsonrpc": "2.0", "method": "Player.GoTo", "params": { "playerid": 1, "position": 1 }, "id": 1}'
	lcd.clear()
	lcd.message("GOTO NEXT")
	player = getActivePlayer()
	if player is not None:
		print player
#		postCmd.format(**player)
		postKodiCommand(postCmd)

def goToPrev():
	# {"jsonrpc": "2.0", "method": "Player.GoTo", "params": { "playerid": 0, "to": "previous" }, "id": 1}
	postCmd = '{"jsonrpc": "2.0", "method": "Player.GoTo", "params": { "playerid": 1, "position": 0 }, "id": 1}'
	lcd.clear()
	lcd.message("GOTO PREV")
	player = getActivePlayer()
	if player is not None:
		print player
#		postCmd.format(**player)
		postKodiCommand(postCmd)

def playPause():
	# {"jsonrpc": "2.0", "method": "Player.PlayPause", "params": { "playerid": 0 }, "id": 1}
	postCmd = '{"jsonrpc": "2.0", "method": "Player.PlayPause", "params": { "playerid": 1 }, "id": 1}'
        player = getActivePlayer()
        if player is not None:
                print player
#                postCmd.format(**player)
                postKodiCommand(postCmd)
	lcd.clear()
	lcd.message("PLAY/PAUSE")

def null_func():
	lcd.clear()
	lcd.message("NULL")

def shutdownScreen():
	global screenOffline 
	screenOffline= True
	lcd.clear()
	lcd.enable_display(False)
	lcd.set_backlight(False)

def resetScreen():
	global screenOffline
	if screenOffline==True:
		screenOffline = False
		lcd.clear()
		lcd.set_color(1,0,0)
		lcd.enable_display(True)
		lcd.set_backlight(True)

buttons = {LCD.SELECT : playPause,
           LCD.LEFT   : goToPrev,
           LCD.UP     : shutdownScreen,
           LCD.DOWN   : null_func,
           LCD.RIGHT  : goToNext }



#############################################################
def main():
	global screenOffline
	screenOffline=True
	resetScreen()
	while True:
		for button in buttons.keys():
			if lcd.is_pressed(button):
				resetScreen()
				buttons[button]()
				while lcd.is_pressed(button):
					pass

if __name__ == '__main__':
	main()
