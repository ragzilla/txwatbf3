"""The WATBF3 (Multi)Service Setup"""

import watweb
import watirc
from watrcon.rconmanager import RconManager
import txmongo
from twisted.internet import defer
from twisted.application.internet import TCPServer
from twisted.application.service import MultiService

class WATBF3Service(MultiService):
	mongo  = None
	config = None
	ic     = None
	rc     = None
	twitt  = None
	
	def __init__(self, config):
		MultiService.__init__(self)
		self.config = config

	@defer.inlineCallbacks
	def startService(self):
		self.mongo = yield txmongo.MongoConnectionPool()
		if self.config['web']['enable']:
			ww = watweb.Application(self, self.config['web'])
			ws = TCPServer(self.config['web']['port'], ww, interface=self.config['web']['bind']).setServiceParent(self)
		if self.config['irc']['enable']:
			self.ic = watirc.getwatircClient(self, self.config['irc'])
			self.ic.setServiceParent(self)
		if self.config['rcon']['enable']:
			self.rc = RconManager(self, self.config['rcon'])
			self.rc.setServiceParent(self)
		if self.config['twitter']['enable']:
			pass # cry
		MultiService.startService(self)
	
	def getRcon(self):
		return self.rc
	
	def getIrc(self):
		return self.ic
	
	def getRootService(self):
		return self
	
	def getMongo(self):
		return self.mongo.watbf3
