from cyclone.web import RequestHandler
from twisted.internet import defer
from resthandler import RestHandler

class ServerHandler(RestHandler):

	@defer.inlineCallbacks
	def get(self, server=None):
		if server:
			server = self.settings['root'].getRcon().getInstance(server)
			if server:
				result = yield server.serverInfo()
				result['players'] = yield server.admin_listPlayers()
				RestHandler.get(self, result)
				return
			self.set_status(404)
		else:
			RestHandler.get(self, self.settings['root'].getRcon().getInstances())
		defer.succeed(None)
		return
