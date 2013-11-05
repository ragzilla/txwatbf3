import cyclone.web
from basehandler import BaseHandler

class SecureHandler(BaseHandler):
	@cyclone.web.authenticated
	def get(self):
		# self.write('authenticated <a href="/auth/logout">logout</a>')
		self.render("secure.html")