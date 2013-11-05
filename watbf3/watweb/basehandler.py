from twisted.internet import defer
import cyclone.web
import session

class BaseHandler(cyclone.web.RequestHandler):
	@defer.inlineCallbacks
	def _execute(self, transforms, *args, **kwargs):
		if isinstance(self, cyclone.web.StaticFileHandler):
			self.session = None
		else:
			self.session = yield self._create_session()
		cyclone.web.RequestHandler._execute(self, transforms, *args, **kwargs)
	
	def finish(self, chunk=None):
		foo = None
		if self.session is not None and self.session._delete_cookie:
			self.clear_cookie(self.settings.get('session_cookie_name', 'session_id'))
		elif self.session is not None:
			self.session.refresh() # advance expiry time and save session
			self.set_secure_cookie(self.settings.get('session_cookie_name', 'session_id'),
				self.session.session_id,
				expires_days=None,
				expires=self.session.expires,
				path=self.settings.get('session_cookie_path', '/'),
				domain=self.settings.get('session_cookie_domain'))
			self.session.save()
		cyclone.web.RequestHandler.finish(self, chunk)

	def get_current_user(self):
		#try:
		#	return cyclone.escape.json_decode(self.get_secure_cookie("user"))
		#except:
		#	return None
		return self.session['user']
	
	@defer.inlineCallbacks
	def _create_session(self):
		settings = self.application.settings # just a shortcut
		session_id = self.get_secure_cookie(settings.get('session_cookie_name', 'session_id'))
		kw = {'security_model': settings.get('session_security_model', []),
			'duration': settings.get('session_age', 900),
			'ip_address': self.request.remote_ip,
			'user_agent': self.request.headers.get('User-Agent'),
			'regeneration_interval': settings.get('session_regeneration_interval', 240)
			}
		new_session = None
		old_session = None

		old_session = yield session.load(session_id, settings.mongo.watbf3.cycloneSessions)
		if old_session is None or old_session._is_expired(): # create new session
			new_session = session.MongoDBSession(settings.mongo.watbf3.cycloneSessions, **kw)
			new_session['user'] = None

		if old_session is not None:
			if old_session._should_regenerate():
				old_session.refresh(new_session_id=True)
				# TODO: security checks
			if 'user' not in old_session.keys():
				old_session['user'] = None
			defer.returnValue(old_session)
		defer.returnValue(new_session)

