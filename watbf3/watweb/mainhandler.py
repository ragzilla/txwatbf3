import cyclone.web
from basehandler import BaseHandler
from twisted.internet import defer


class MainHandler(BaseHandler):

	@defer.inlineCallbacks
	def get(self):
		self.write('FUCK')
