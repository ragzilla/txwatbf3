import cyclone.web
from basehandler import BaseHandler

class ErrorHandler(BaseHandler):
	def __init__(self, application, request, status_code):
		cyclone.web.RequestHandler.__init__(self, application, request)
		self.set_status(status_code)

	def send_error(self, status_code=500, **kwargs):
		if self._headers_written:
			log.err("Cannot send error response after headers written")
			if not self._finished:
				self.finish()
			return
		self.clear()
		self.set_status(status_code)
		e = kwargs.get("exception")
		if isinstance(e, cyclone.web.HTTPAuthenticationRequired):
			args = ",".join(['%s="%s"' % (k, v) for k, v in e.kwargs.items()])
			self.set_header("WWW-Authenticate", "%s %s" % (e.auth_type, args))
		try:
			self.render("error.html", status_code=status_code)
		except Exception:
			logging.error("Uncaught exception in ErrorHandler.send_error")
		if not self._finished:
			self.finish()
	
	def prepare(self):
		raise cyclone.web.HTTPError(self._status_code)