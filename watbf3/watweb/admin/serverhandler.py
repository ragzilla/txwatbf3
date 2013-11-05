import cyclone.web
from twisted.internet import defer
from ..basehandler import BaseHandler

from wtforms import Form, TextField, IntegerField, validators

class ServerForm(Form):
	name   = TextField("Server Name", [validators.Required()])
	ip     = TextField("IP",          [validators.IPAddress()])
	port   = IntegerField("Port",     [validators.NumberRange(min=1025, max=65535)])
	secret = TextField("Secret",      [validators.Required()])

class ServerHandler(BaseHandler):
	@cyclone.web.authenticated
	@defer.inlineCallbacks
	def get(self):
		watbf3 = self.settings.mongo.watbf3
		servers = yield watbf3.servers.find()
		e = self.get_argument("e", None)
		errormsg=(e == "invalid" and "<br/>Invalid server." or "")
		self.render("admin-server-get.html", servers=servers, errormsg=errormsg)
	
	@defer.inlineCallbacks
	def post(self):
		watbf3 = self.settings.mongo.watbf3
		