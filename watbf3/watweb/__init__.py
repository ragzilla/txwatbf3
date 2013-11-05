import os
import cyclone.web
from twisted.application.internet import TimerService
from mainhandler import MainHandler

class Application(cyclone.web.Application):
	config = None

	def __init__(self, config):
		handlers = [
			(r"/", MainHandler),
			]
		settings = dict(
			config = config
			template_path=os.path.abspath(os.path.join(os.path.dirname(__file__), "templates")),
			static_path=os.path.abspath(os.path.join(os.path.dirname(__file__), "static")),
			xheaders = True,
			xsrf_cookies=True,
			debug = True,
			)
		cyclone.web.Application.__init__(self, handlers, **settings)
