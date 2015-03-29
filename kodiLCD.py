
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

CHAR_PAUSE = 1
CHAR_PLAY = 2

class NowPlayingThread(threading.Thread):
	def __init__(self):
		super(NowPlayingThread,self).__init__()
		self.item={}
		self.checkMode()
		self.title = ''
		self.artist = ''
		self.duration = ''
		self.elapsed = ''

	def checkMode(self):
		player = getActivePlayer()
		if player is None:
			self.mode=MODE_NONE
		elif player['type'] == 'video':
			self.mode=MODE_VIDEO
		elif player['type'] == 'audio':
			self.mode=MODE_AUDIO
		else:
			self.mode=MODE_NONE

	def run(self):
		while True:
			# {"jsonrpc": "2.0", "method": "Player.GetProperties", "params": {"properties": ["percentage", "playlistid", "type", "time", "totaltime"], "playerid": 1 }, "id": 1}
			# {"jsonrpc": "2.0", "method": "Player.GetItem", "params": { "properties": ["title", "album", "artist", "duration"], "playerid": 0 }, "id": "AudioGetItem"}
			# {"jsonrpc": "2.0", "method": "Player.GetItem", "params": { "properties": ["title", "artist", "season", "episode", "duration", "showtitle"], "playerid": 1 }, "id": "VideoGetItem"}
			
			time.sleep(0.25)
	def getArtist(self):
		return self.artist

	def getTitle(self):
		return self.title

	def getDuration(self):
		return self.duration

	def getElapsed(self):
		return self.elapsed
		

class DisplayThread(threading.Thread):
	def __init__ (self):
		super(DisplayThread,self).__init__()
		self.PriorityMessage= False
		self.tick=0

	def run(self):
		while True:
			if not self.PriorityMessage:
				if getActivePlayer() is not None:
					strings = self.buildText()
					lcd.home()
					lcd.message(strings[0])
					lcd.set_cursor(0,1)
					lcd.message(strings[1])
					time.sleep(.33)	
					self.tick += 1
			else:
				time.sleep(3.0)

	def message(self,message):
		self.PriorityMessage = True
		lcd.clear()
		lcd.message(message)
		threading.Timer(3,self.__messageTimeout).start()

	def __messageTimeout(self):
		self.PriorityMessage = False

	def buildText(self):
		title = self.getFormattedTitleString()
		playing = self.isPlaying()
		time = self.getFormattedTimeString()
		artist = self.getFormattedArtistString(time)
		playcode = ''
		if playing:
			playcode = '\x02'
		else:
			playcode = '\x01'
		titleSpace = 15 - len(title)
		artistSpace = 16 - len(artist) - len(time) 
		hiRow = title + (" " * titleSpace) + playcode
		loRow = artist + (" "* artistSpace) + time
		return [hiRow,loRow]

	def getFormattedTitleString(self):
		title = playing_thread.getTitle()
		return self.getCycleSubstring(title,14)

	def getFormattedTimeString(self):
		return "11:22"

	def getFormattedArtistString(self,time):
		avaspace = (16 - len(time) - 1) 
		artist = playing_thread.getArtist()
		if(len(artist) < avaspace):
			return artist
		
		return self.getCycleSubstring(artist,avaspace)
		
	def isPlaying(self):
		return False

	def resetScroll(self):
		self.tick = 0
	

	def getCycleSubstring(self,string,length):
		cycleString = string + ' ' + string
		strlen = len(string)
		startchar = self.tick % (strlen + 1)
		return cycleString[startchar:startchar+length]

	
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
	lcd.create_char(CHAR_PLAY,[0,8,12,14,12,8,0,0])
	lcd.create_char(CHAR_PAUSE,[0,27,27,27,27,27,0,0])
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
