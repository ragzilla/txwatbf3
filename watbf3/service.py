"""The WATBF3 (Multi)Service Setup"""

import watweb
import watirc
import watrcon
import txmongo
from twisted.internet import defer
from twisted.application.internet import TCPServer
from twisted.application.service import MultiService

class WATBF3Service(MultiService):
	mongo   = None
	options = None
	rc      = None
	
	def __init__(self, options):
		MultiService.__init__(self)
		self.options = options

	@defer.inlineCallbacks
	def startService(self):
		self.mongo = yield txmongo.MongoConnectionPool()
		ww = watweb.Application(self.mongo)
		ic = watirc.getwatircClient(self.mongo, self).setServiceParent(self)
		ws = TCPServer(self.options['webport'], ww, interface="0.0.0.0").setServiceParent(self)
		ss = ww.getSessionService().setServiceParent(self)
		rc = watrcon.getRconManager()
		rc.setServiceParent(self)
		self.rc = rc
		MultiService.startService(self)
	
	def getRcon(self):
		return self.rc
	
	def getRootService(self):
		return self
	
	def getMongo(self):
		return self.mongo.watbf3
