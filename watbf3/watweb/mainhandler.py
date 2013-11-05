from cyclone.web import RequestHandler
from twisted.internet import defer


class MainHandler(RequestHandler):

	@defer.inlineCallbacks
	def get(self):
		self.write('FUCK')
