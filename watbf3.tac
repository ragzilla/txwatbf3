#! /home/ragnar/.virtualenvs/watbf3/bin/twistd -noy
# vim: syntax=python

"""
This is the watbf3.tac file. This will start up the watbf3 application.
"""

from twisted.application import service
from watbf3.service import WATBF3Service
from twisted.python import usage
from yaml import safe_load as yaml_load

config = {
	'irc':     { 'enable': False, },
	'rcon':    { 'enable': False, },
	'twitter': { 'enable': False, },
	'web':     { 'enable': False, },
	'stats':   { 'enable': False, },
}
siteconfig = yaml_load(open('watbf3.yaml'))
config.update(siteconfig)

application = service.Application("Web Admin Tool - BF3")
watbf3 = WATBF3Service(config)
watbf3.setServiceParent(application)
