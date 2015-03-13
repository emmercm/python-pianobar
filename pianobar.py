import datetime
import pexpect
import re

class pianobar(object):
	_pianobar = None
	
	def __init__(self, *args):
		pass
		
	def Start(self):
		self._pianobar = pexpect.spawn("pianobar")
		try:
			self._pianobar.expect_exact("Welcome to pianobar", timeout=5)
		except pexpect.ExceptionPexpect:
			return False
		return True
			
	def Exit(self):
		return self.Send("q")
			
			
	def IsRunning(self):
		try:
			return self._pianobar.isalive()
		except pexpect.ExceptionPexpect:
			return False
			
	def Buffer(self):
		try:
			return self._pianobar.before
		except pexpect.ExceptionPexpect:
			return ""
			
	def Send(self, str):
		try:
			self._pianobar.send(str)
			return True
		except pexpect.ExceptionPexpect:
			return False
			
		
	def Play(self):
		return self.Send("P")
			
	def Pause(self):
		return self.Send("S")
			
	def Next(self):
		return self.Send("n")
			
		
	def Login(self, email, password):
		try:
			self._pianobar.expect_exact("Email:", timeout=1)
			self._pianobar.sendline(email)
			self._pianobar.expect_exact("Password:", timeout=1)
			self._pianobar.sendline(password)
			self._pianobar.expect_exact("Login... Ok.", timeout=5)
		except pexpect.ExceptionPexpect:
			return False
		return True
		
		
	def ListStations(self):
		stations = {}
		try:
			self._pianobar.sendline("s\b")
			self._pianobar.expect_exact("Select station:", timeout=1)
			for line in self.Buffer().splitlines():
				if re.search("\s+[0-9]+\)\s+", line) is not None: # match " #) "
					station_id = line[4:7].strip()
					station_name = line[13:].strip()
					stations[station_id] = station_name
		except pexpect.ExceptionPexpect:
			pass
		return stations
		
	def ChangeStation(self, station_id):
		try:
			self.Send("s\b")
			self._pianobar.sendline(str(station_id))
			self._pianobar.expect_exact("Receiving new playlist... Ok", timeout=5)
			return True
		except pexpect.ExceptionPexpect:
			return False
			
			
	def GetInfo(self):
		trackinfo = {}
		re_track = re.compile(".*\"(.+?)\" by \"(.+?)\" on \"(.+?)\".*", re.IGNORECASE)
		re_progress = re.compile("-([\:0-9]+)/([\:0-9]+)")
		try:
			self.Send("i\b")
			self._pianobar.expect("Station", timeout=1)
			for line in self.Buffer().splitlines():
				track = re_track.findall(line)
				if len(track) > 0:
					trackinfo = dict(trackinfo.items() + {"artist":track[0][1], "title":track[0][0], "album":track[0][2]}.items())
				progress = re_progress.findall(line)
				if len(progress) > 0:
					remaining = datetime.datetime.strptime(progress[0][0],"%M:%S")
					remaining = remaining.minute*60 + remaining.second
					length = datetime.datetime.strptime(progress[0][1],"%M:%S")
					length = length.minute*60 + length.second
					trackinfo = dict(trackinfo.items() + {"elapsed":(length-remaining), "length":length}.items())
		except pexpect.ExceptionPexpect:
			pass
		return trackinfo