from cyclone.web import RequestHandler
from simplejson import dumps as json_dumps

class RestHandler(RequestHandler):
	def get(self, content):
		callback = self.get_argument("callback", None)
		if type(content) is not dict:
			content = { 'content': content }
		if callback:
			self.set_header('Content-Type', 'application/javascript')
			self.write(callback + '(' + json_dumps(content) + ');')
		else:
			self.set_header('Content-Type', 'application/json')
			self.write(json_dumps(content, sort_keys=True, indent=4 * ' '))
		
