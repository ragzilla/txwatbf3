from cyclone.web import RequestHandler
from twisted.internet import defer
from resthandler import RestHandler

class MainHandler(RestHandler):

	# @defer.inlineCallbacks
	def get(self):
		RestHandler.get(self, {'app':'watbf3','version':'0.1'})
		# defer.succeed(None)
