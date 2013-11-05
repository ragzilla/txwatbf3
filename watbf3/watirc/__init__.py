"""
watirc, a pyfibot based irc client, for watbf3
"""

import os
import time
import socket
import logging
import string
from twisted.names import client
from twisted.internet import defer, ssl
from twisted.words.protocols import irc
from twisted.application.internet import SSLClient
from pyfibot.pyfibot import PyFiBotFactory
from pyfibot.botcore import PyFiBot
from fnmatch import fnmatch

log = logging.getLogger("watircbot")

class Network():
	def __init__(self, root, alias, address, nickname, channels=None, linerate=None, password=None, is_ssl=False, data={}):
		self.alias = alias
		self.address = address
		self.nickname = nickname
		self.channels = channels or {}
		self.linerate = linerate
		self.password = password
		self.is_ssl = is_ssl
		self.data = data

class watircBot(PyFiBot):
	def __init__(self, network):
		self.password = network.password
		self.CMDCHAR = "!"
		PyFiBot.__init__(self, network)

	def command_help(self, user, channel, cmnd):
		"""Get help on all commands or a specific one. Usage: help [<command>]"""

		commands = []
		for module, env in self.factory.ns.items():
			myglobals, mylocals = env
			commands += [(c.replace("command_", ""), ref) for c, ref in mylocals.items() if c.startswith("command_%s" % cmnd)]
			commands += [(c.replace("inlinecommand_", ""), ref) for c, ref in mylocals.items() if c.startswith("inlinecommand_%s" % cmnd)]
		# Help for a specific command
		if len(cmnd) > 0:
			for cname, ref in commands:
				if cname == cmnd:
					helptext = ref.__doc__.split("\n", 1)[0]
					self.say(channel, "Help for %s: %s" % (cmnd, helptext))
					return
		# Generic help
		else:
			commandlist = ", ".join([c for c, ref in commands])
			self.say(channel, "Available commands: %s" % commandlist)
	
	def replyto(self, user, channel):		
		return (channel.lower() == self.nickname.lower()) and self.factory.getNick(user) or channel

	def connectionMade(self):
		irc.IRCClient.connectionMade(self)
		self.repeatingPing(30)
		log.info("connection made")
		### set up a subscription
		rc    = self.network.data["root"].getRcon()
		rc.subMessage("servers.kfs3.server.onLevelLoaded", self.onLevelLoaded)
		rc.subMessage("servers.kfs3.player.onJoin", self.onJoin)
		rc.subMessage("servers.kfs3.player.onChat", self.onChat)
	
	def sendNotify(self, message):
		### a shortcut for event driven stuff
		self.say(self.network.data["notify"], str(message))
	
	# rcon level load callback
	def onLevelLoaded(self, params):
		self.sendNotify("MAPCHANGE: %(level)s (%(mode)s) [Round %(curRound)u/%(maxRound)u]" % params)
	
	def onJoin(self, params):
		# if params['isgoon']:
			# self.sendNotify("GOONJOIN: %(player)s" % params)
			isgoon = params['isgoon'] # nullop without using pass
	
	def onChat(self, params):
		# self.sendNotify("%(player)s: %(message)s" % params)
		foo = params # nullop
	
	@defer.inlineCallbacks
	def _command(self, user, channel, cmnd):
		PyFiBot._command(self, user, channel, cmnd)
		# check for inline commands
		try:
			cmnd, args = cmnd.split(" ", 1)
		except ValueError:
		    args = ""
		for module, env in self.factory.ns.items():
			myglobals, mylocals = env
			commands = [(c, ref) for c, ref in mylocals.items() if c == "inlinecommand_%s" % cmnd]
			for cname, command in commands:
				log.info("module inlinecommand %s called by %s (%s) on %s" % (cname, user, self.factory.isAdmin(user), channel))
				res = yield command(self, user, channel, args)
	
	def privmsg(self, user, channel, msg):
		"""This will get called when the bot receives a message.
		@param user: nick!user@host
		@param channel: Channel where the message originated from
		@param msg: The actual message
		"""

		channel = channel.lower()
		lmsg = msg.lower()
		lnick = self.nickname.lower()
		nickl = len(lnick)
		if channel == lnick:
			# Turn private queries into a format we can understand
			if not msg.startswith(self.CMDCHAR):
				msg = self.CMDCHAR + msg
			elif lmsg.startswith(lnick):
				msg = self.CMDCHAR + msg[nickl:].lstrip()
			elif lmsg.startswith(lnick) and len(lmsg) > nickl and lmsg[nickl] in string.punctuation:
				msg = self.CMDCHAR + msg[nickl + 1:].lstrip()
		else:
			# Turn 'nick:' prefixes into self.CMDCHAR prefixes
			if lmsg.startswith(lnick) and len(lmsg) > nickl and lmsg[nickl] in string.punctuation:
				msg = self.CMDCHAR + msg[len(self.nickname) + 1:].lstrip()
		reply = self.replyto(user, channel)

		if msg.startswith(self.CMDCHAR):
			cmnd = msg[len(self.CMDCHAR):]
			self._command(user, reply, cmnd)

		# Run privmsg handlers
		self._runhandler("privmsg", user, reply, msg)

class watircFactory(PyFiBotFactory):
	protocol  = watircBot
	moduledir = os.path.join(os.path.dirname(__file__), "modules/")
	
	def createNetwork(self, address, alias, nickname, channels=None, linerate=None, password=None, is_ssl=False, data={}):
		self.setNetwork(Network(None, alias, address, nickname, channels, linerate, password, is_ssl, data))

	def isAdmin(self, user):
		"""Check if an user has admin privileges.
		@return: True or False"""
		for pattern in self.config['admins']:
			if fnmatch(user.lower(), pattern.lower()):
				return True
		return False

class logHandler(logging.Handler):
	def emit(self, record):
		print self.format(record)

def getwatircClient(mongo, root):
	# create a stdio logger or something
	logger  = logging.getLogger()
	handler = logHandler()
	handler.setFormatter(logging.Formatter("[%(name)s] %(message)s"))
	logger.addHandler(handler)
	logger.setLevel(logging.INFO)
	
	config = {'nick': 'whammy', 
			  'admins': [
			  	'ragzilla!ragzilla@evilgeni.us',
				'daveslash!daveslash@could.you.not',
				'dannyb!~dannyb@thanks.for.this',
				'nfcknblvbl!~nfcknblvb@*.hsd1.ga.comcast.net',
			  ], 
			  'networks': {
				'synirc': {
				  'channels': ['#goonwhores'], 
				  'linerate': 1, 
				  'server': 'x', 
				  'port': 6667, 
				  'is_ssl': True,
				  'password': 'x',
				  'data': {
				        "services.user":     "NickServ!services@services.synirc.net",
				        "services.password": "x",
					"mongo":  mongo,
					"root":   root,
					"tag":    "kfs3",
					"notify": "#goonwhores",
				    },
				  }
				}
			  }
	factory = watircFactory(config)
	for network, settings in config['networks'].items():
		# settings = per network, config = global
		nick = settings.get('nick', None) or config['nick']
		linerate = settings.get('linerate', None) or config.get('linerate', None)
		password = settings.get('password', None)
		is_ssl = bool(settings.get('is_ssl', False))
		port = int(settings.get('port', 6667))
		data = dict(settings.get('data', {}))

		# normalize channel names to prevent internal confusion
		chanlist = []
		for channel in settings['channels']:
			if channel[0] not in '&#!+':
				channel = '#' + channel
			chanlist.append(channel)
		# resolve server name here in case it's a round-robin address
		server_name = socket.getfqdn(settings['server'])
		factory.createNetwork((server_name, port), network, nick, chanlist, linerate, password, is_ssl, data)
		return SSLClient(server_name, port, factory, ssl.ClientContextFactory())
