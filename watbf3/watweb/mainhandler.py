import cyclone.web
from basehandler import BaseHandler
from twisted.internet import defer


class MainHandler(BaseHandler):

	@defer.inlineCallbacks
	def get(self):
		gooncnt = yield self.settings.mongo.watbf3.bf3names.count()
		self.render("index.html", gooncnt=int(gooncnt))
