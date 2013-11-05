import bcrypt
import cyclone.web
from twisted.internet import defer
from basehandler import BaseHandler

class LoginHandler(BaseHandler):
	def get(self):
		if self.session['user'] is not None:
			self.redirect("/")
			return
		e = self.get_argument("e", None)
		try:
			n = self.get_argument("next")
		except:
			n = None
		self.render("login.html", 
			n=(n != None and n or "/"), 
			errormsg=(e == "invalid" and "invalid username or password" or "")
			)
	
	@defer.inlineCallbacks
	def post(self):
		if self.session['user'] is not None:
			self.redirect("/")
			return
		try:
			u, p, n = self.get_argument("u"), self.get_argument("p"), self.get_argument("n")
		except:
			self.redirect("/auth/login?e=invalid")
			return
		try:
			user = yield self.settings.mongo.watbf3.users.find_one({"username" : u})
		except Exception, e:
			log.err("mongo can't find user %s: %s" % (u, e))
			raise cyclone.web.HTTPError(503)

		if user:
			if bcrypt.hashpw(p, user["password"]) == user["password"]:
				user["_id"] = str(user["_id"])
				# self.set_secure_cookie("user", cyclone.escape.json_encode(user))
				self.session['user'] = user
				self.redirect(n)
			else:
				self.redirect("/auth/login?e=invalid")
		else:
			self.redirect("/auth/login?e=invalid")