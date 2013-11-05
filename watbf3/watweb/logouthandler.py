import cyclone.web
from basehandler import BaseHandler

class LogoutHandler(BaseHandler):
	@cyclone.web.authenticated
	def get(self):
		if self.session is not None:
			self.session.invalidate()
		self.redirect("/")
