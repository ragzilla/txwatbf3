import os
import cyclone.web
from mainhandler import MainHandler

class Application(cyclone.web.Application):
	config = None

	def __init__(self, root, config):
		handlers = [
			(r"/", MainHandler),
			]
		settings = dict(
			root = root,
			config = config,
			template_path=os.path.abspath(os.path.join(os.path.dirname(__file__), "templates")),
			static_path=os.path.abspath(os.path.join(os.path.dirname(__file__), "static")),
			xheaders = True,
			xsrf_cookies=True,
			debug = True,
			)
		cyclone.web.Application.__init__(self, handlers, **settings)
