#! /home/ragnar/.virtualenvs/watbf3/bin/twistd -noy

"""
This is the watbf3.tac file. This will start up the watbf3 application.
"""

from twisted.application import service
from watbf3.service import WATBF3Service
from twisted.python import usage

class Options(usage.Options):
	optParameters = [
		["webport", "w", 80, None, int],
		["irchost", "ih", "us.synirc.net", None, str],
		["ircport", "ip", 7001, None, str],
		["ircssl",  "is", True, None, bool],
	]
options = Options()
options.parseOptions([])

application = service.Application("Web Admin Tool - BF3")
watbf3 = WATBF3Service(options)
watbf3.setServiceParent(application)
