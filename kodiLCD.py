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

CHAR_PAUSE = 0
CHAR_PLAY = 1

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
	def onPauseResume(self):
		pass

class DisplayThread(threading.Thread):
	def __init__ (self):
		super(DisplayThread,self).__inti__()
		self.PriorityMessage= False
	def run(self):
		while True:
			if not self.PriorityMessage:
				lcd.clear()
				strings = self.buildText()
				lcd.home()
				lcd.message(strings[0])
				lcd.set_cursor(0,1)
				lcd.message(strings[1])
				time.sleep(.33)	
			else
				time.sleep(3.0)

	def message(self,message):
		self.PriorityMessage = True
		lcd.clear()
		lcd.message(message)
		threading.Timer(3,self.__messageTimeout).start()

	def __messageTimeout(self):
		self.PriorityMessage = False

	def buildText(self):
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
	display_thread.message("GOTO NEXT")
	player = getActivePlayer()
	if player is not None:
		print player
		postKodiCommand(postCmd)

def goToPrev():
	# {"jsonrpc": "2.0", "method": "Player.GoTo", "params": { "playerid": 0, "to": "previous" }, "id": 1}
	postCmd = '{"jsonrpc": "2.0", "method": "Player.GoTo", "params": { "playerid": 1, "position": 0 }, "id": 1}'
	lcd.clear()
	display_thread.message("GOTO PREV")
	player = getActivePlayer()
	if player is not None:
		print player
		postKodiCommand(postCmd)

def playPause():
	# {"jsonrpc": "2.0", "method": "Player.PlayPause", "params": { "playerid": 0 }, "id": 1}
	postCmd = '{"jsonrpc": "2.0", "method": "Player.PlayPause", "params": { "playerid": 1 }, "id": 1}'
        player = getActivePlayer()
        if player is not None:
                print player
                postKodiCommand(postCmd)
		playing_thread.onPauseResume()
	lcd.clear()
	display_thread.message("PLAY/PAUSE")

def null_func():
	lcd.clear()
	display_thread.message("NULL")

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
		lcd.enable_display(True)
		lcd.set_backlight(True)
		lcd.set_color(1.0,0.0,0.0)
		print 'resetting screen'

buttons = {LCD.SELECT : playPause,
           LCD.LEFT   : goToPrev,
           LCD.UP     : shutdownScreen,
           LCD.DOWN   : null_func,
           LCD.RIGHT  : goToNext }


playing_thread = NowPlayingThread()
display_thread = DisplayThread()
#############################################################
def main():
	global screenOffline
	global playing_thread
	global display_thread
	lcd.create_char(CHAR_PLAY,[0,8,12,14,12,8,0])
	lcd.create_char(CHAR_PAUSE,[0,27,27,27,27,27,0])
	playing_thread.start()
	display_thread.start()
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
