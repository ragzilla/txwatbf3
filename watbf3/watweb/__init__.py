import os
import cyclone.web
from twisted.application.internet import TimerService
from basehandler import BaseHandler
from goonreghandler import GoonregHandler
from errorhandler import ErrorHandler
from loginhandler import LoginHandler
from logouthandler import LogoutHandler
from mainhandler import MainHandler
from securehandler import SecureHandler
from admin.serverhandler import ServerHandler as AdminServerHandler

class Application(cyclone.web.Application):
	def __init__(self, db):
		cyclone.web.ErrorHandler = ErrorHandler

		handlers = [
			(r"/", MainHandler),
			(r"/auth/login", LoginHandler),
			(r"/auth/logout", LogoutHandler),
			(r"/secure", SecureHandler),
			(r"/goonreg", GoonregHandler),
			(r"/admin/server", AdminServerHandler),
			]
		settings = dict(
			login_url = "/auth/login",
			cookie_secret = "igSjp1WmQF6Hpkg2wBvbvlcgts3om0X6kUk5fLRyOcs=",
			mongo = db,
			template_path=os.path.abspath(os.path.join(os.path.dirname(__file__), "../../templates")),
			static_path=os.path.abspath(os.path.join(os.path.dirname(__file__), "../../static")),
			xheaders = True,
			xsrf_cookies=True,
			debug = True,
			)
		cyclone.web.Application.__init__(self, handlers, **settings)
	
	def getSessionService(self):
		return TimerService(30, session.delete_expired, self.settings['mongo'].watbf3.cycloneSessions)