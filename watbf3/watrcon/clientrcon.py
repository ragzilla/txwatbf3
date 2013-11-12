import os
import base64
import hashlib
from datetime import datetime  
from cyclone.httpclient import fetch
from simplejson import dumps
from twisted.internet import defer
from twisted.internet.defer import Deferred
from twisted.internet.protocol import ReconnectingClientFactory
from serverstate.server import Server
from math import floor

from fbrcon import FBRconFactory, FBRconProtocol

def getClientRconFactory(params, rm):
	factory = ClientRconFactory(False, params, rm)
	factory.protocol = ClientRconProtocol
	return factory

class ClientRconFactory(ReconnectingClientFactory, FBRconFactory):
	ReconnectingClientFactory.maxdelay = 15
	ReconnectingClientFactory.factor = 1.6180339887498948
	rm = None
	instance = None
	
	def __init__(self, isServer = False, params = {}, rm = None):
		self.rm = rm
		FBRconFactory.__init__(self, isServer, params)
	
	def buildProtocol(self, addr):
		p = self.protocol()
		p.factory = self
		self.instance = p
		return p
		
levelhash = {
	'MP_Abandoned': { 'name': 'Zavod 311',          'factions': ['US', 'RU'] },
	'MP_Damage':    { 'name': 'Lancang Dam',        'factions': ['RU', 'CN'] },
	'MP_Flooded':   { 'name': 'Flood Zone',         'factions': ['US', 'CN'] },
	'MP_Journey':   { 'name': 'Golmud Railway',     'factions': ['RU', 'CN'] },
	'MP_Naval':     { 'name': 'Paracel Storm',      'factions': ['US', 'CN'] },
	'MP_Prison':    { 'name': 'Operation Locker',   'factions': ['US', 'RU'] },
	'MP_Resort':    { 'name': 'Hainan Resort',      'factions': ['US', 'CN'] },
	'MP_Siege':     { 'name': 'Siege of Shanghai',  'factions': ['US', 'CN'] },
	'MP_TheDish':   { 'name': 'Rogue Transmission', 'factions': ['RU', 'CN'] },
	'MP_Tremors':   { 'name': 'Dawnbreaker',        'factions': ['US', 'CN'] },
}

modehash = {
	'ConquestLarge0': 'Conquest',
	'ConquestAssaultLarge0': 'Conquest Assault',
	'ConquestSmall0': 'Consolequest',
	'Domination0':    'Domination',
	'Elimination0':   'Defuse',
	'Obliteration':   'Obliteration',
	'RushLarge0':     'Rush',
	'SquadRush0':     'Squad Rush',
	'SquadDeathMatch0': 'Squad Deathmatch',
	'TeamDeathMatch0':  'Team Deathmatch',
}

class ClientRconProtocol(FBRconProtocol):
	"""a unique instance of this spawns for each rcon connection. i think."""
	
	def __init__(self):
		FBRconProtocol.__init__(self)
		# need to move some (all?) of these handlers into the parent class, or a mixin, should probably evict the 
		# modehash/levelhash too
		self.handlers = {
			"player.onJoin":          self.player_onJoin,
			"player.onLeave":         self.player_onLeave,
			"player.onAuthenticated": self.player_onAuthenticated,
			"player.onChat":          self.player_onChat,
			"player.onTeamChange":    self.player_onTeamChange,
			"player.onSquadChange":   self.player_onSquadChange,
			"player.onKill":          self.nullop, # temporary
			"server.onLevelLoaded":   self.server_onLevelLoaded,
			"punkBuster.onMessage":   self.nullop,
			"player.onSpawn":         self.nullop,
			"version":                self.nullop,
			"serverInfo":             self.nullop,
			"listPlayers":            self.nullop,
			"server.onRoundOver":     self.nullop,
			"server.onRoundOverPlayers": self.nullop,
			"server.onRoundOverTeamScores": self.nullop,
			"login.hashed": self.nullop,
			"admin.say": self.nullop,
			"vars.preset": self.nullop,
		}
		self.seq = 1
		self.callbacks = {}
		self.server = Server(self)
	
	### OK <serverName: string> <current playercount: integer> <effective max playercount: integer> <current gamemode: string> 
	### <current map: string> <roundsPlayed: integer> <roundsTotal: string> <scores: team scores> <onlineState: online state> 
	### <ranked: boolean> <punkBuster: boolean> <hasGamePassword: boolean> <serverUpTime: seconds> <roundTime: seconds> 
	### <gameIpAndPort: IpPortPair> <punkBusterVersion: string> <joinQueueEnabled: boolean> <region: string> 
	### <closestPingSite: string> <country: string> <matchMakingEnabled: boolean> <blazePlayerCount: integer> 
	### <blazeGameState: string> 
	@defer.inlineCallbacks
	def serverInfo(self):
		sinfo = yield self.sendRequest(["serverInfo"])
		retval = {
			'serverName': sinfo[1],
			'curPlayers': int(sinfo[2]),
			'maxPlayers': int(sinfo[3]),
			'mode': modehash[sinfo[4]],
			'level': levelhash[sinfo[5]]['name'],
			'roundsPlayed': int(sinfo[6]) + 1,
			'roundsTotal': int(sinfo[7]),
			'numTeamScores': int(sinfo[8]),
		}
		# process team scores

		if retval['numTeamScores'] == 2:
			retval['teams'] = [
				{ 'faction': levelhash[sinfo[5]]['factions'][0], 'score': int(floor(float(sinfo[9])))},
				{ 'faction': levelhash[sinfo[5]]['factions'][1], 'score': int(floor(float(sinfo[10])))},
			]
		else:
			retval['teams'] = []

		off = 9 + retval['numTeamScores'] # 9 = offset + 1 to get us past the teamScores
		retval.update({
			'targetScore':       int(sinfo[off+0]),
			'onlineState':       sinfo[off+1],
			'ranked':            sinfo[off+2] == 'true',
			'punkBuster':        sinfo[off+3] == 'true',
			'hasGamePassword':   sinfo[off+4] == 'true',
			'serverUpTime':      int(sinfo[off+5]),
			'roundTime':         int(sinfo[off+6]),
			'gameIpAndPort' :    sinfo[off+7],
			'punkBusterVersion': sinfo[off+8],
			'joinQueueEnabled':  sinfo[off+9] == 'true',
			'region':            sinfo[off+10],
			'closestPingSite':   sinfo[off+11],
			'country':           sinfo[off+12],
			# 'matchMakingEnabled' # not enabled yet?
			'blazePlayerCount':  int(sinfo[off+13]),
			'blazeGameState':    sinfo[off+14],
		})
		defer.returnValue(retval)
	
	def nullop(self, packet):
		pass

	### IsFromClient,  Response,  Sequence: 2  Words: "OK" "7" "name" "guid" "teamId" "squadId" "kills" "deaths" "score" "0" 
	@defer.inlineCallbacks
	def admin_listPlayers(self):
		players = yield self.sendRequest(["admin.listPlayers", "all"])
		retval = {}
		fields = []
		status = players.pop(0)
		numparams = int(players.pop(0)) 
		for i in range(numparams):
			fields.append(players.pop(0))
		numplayers = int(players.pop(0))
		for i in range(numplayers):
			tmp = {}
			for val in fields:
				tmp[val] = players.pop(0)
			retval[tmp['name']] = tmp
		# print "listPlayers:",retval
		defer.returnValue(retval)
	
	@defer.inlineCallbacks
	def admin_listOnePlayer(self, player):
		players = yield self.sendRequest(["admin.listPlayers", "player", player])
		retval = None
		fields = []
		status = players.pop(0)
		numparams = int(players.pop(0)) 
		for i in range(numparams):
			fields.append(players.pop(0))
		numplayers = int(players.pop(0))
		tmp = {}
		for val in fields:
			tmp[val] = players.pop(0)
		retval = tmp
		defer.returnValue(retval)

	@defer.inlineCallbacks
	def admin_kickPlayer(self, player, reason):
		retval = yield self.sendRequest(["admin.kickPlayer", player, reason])

	@defer.inlineCallbacks
	def admin_killPlayer(self, player):
		retval = yield self.sendRequest(["admin.killPlayer", player])
	
	@defer.inlineCallbacks
	def admin_say(self, message, players):
		retval = yield self.sendRequest(["admin.say", message, players])
	
	### Unhandled event: IsFromServer, Request, Sequence: 132, Words: "server.onLevelLoaded" "MP_007" "ConquestLarge0" "0" "2"
	def server_onLevelLoaded(self, packet): 
		params = {
		'level':    levelhash[packet.words[1]]['name'],
		'mode':     modehash[packet.words[2]],
		'curRound': int(packet.words[3]) + 1,
		'maxRound': int(packet.words[4]),
		}
		self.postMessage("server.onLevelLoaded", params)

	@defer.inlineCallbacks
	def player_onJoin(self, packet):
		normal = str(packet.words[1]).lower()
		isgoon = yield self.mongo.bf3names.count({'bf3name': normal})
		self.postMessage("player.onJoin", {'player': packet.words[1], 'guid': packet.words[2], 'isgoon': isgoon != 0})

	def player_onAuthenticated(self, packet):
		self.postMessage("player.onAuthenticated", {'player': packet.words[1]})
		
	def player_onLeave(self, packet):
		self.postMessage("player.onLeave", {'player': packet.words[1]})
	
	@defer.inlineCallbacks
	def player_onChat(self, packet):
		self.postMessage("player.onChat", {'player': packet.words[1], 'message': packet.words[2]})
		# should probably refactor this into a plugin, but oh well
		utcnow = datetime.utcnow()
		url = strftime('http://localhost:9200/watbf3-%Y%m%d/onchat/')
		msg = dumps({'player': packet.words[1], 'message': packet.words[2], 'timestamp': utcnow.isoformat() + 'Z'})
		retval = yield fetch(url, postdata=msg)
	
	# "player.onTeamChange" "toomuchmoney678" "2" "0"
	def player_onTeamChange(self, packet):
		pass
	
	# "player.onSquadChange" "toomuchmoney678" "2" "3"
	def player_onSquadChange(self, packet):
		pass
		
	@defer.inlineCallbacks
	def connectionMade(self):
		self.params = self.factory.params
		self.mongo  = self.factory.rm.mongo
		FBRconProtocol.connectionMade(self)
		ver   = yield self.sendRequest(["version"])
		salt  = yield self.sendRequest(["login.hashed"])
		m = hashlib.md5()
		m.update(salt[1].decode("hex"))
		m.update(self.factory.params["secret"])
		login = yield self.sendRequest(["login.hashed", m.digest().encode("hex").upper()])
		event = yield self.sendRequest(["admin.eventsEnabled", "true"])
		players = yield self.admin_listPlayers()
		for player in players:
			pl = players[player]
			ph = self.server.addPlayer(pl['name'], pl['guid'])
		self.postMessage("status", "connectionMade")
		self.factory.resetDelay()
	
	def postMessage(self, facility, message):
		self.factory.rm.postMessage("servers.%s.%s" % (self.params["tag"], facility), message)
	
	def connectionLost(self, reason):
		self.postMessage("status", "connectionLost")
		FBRconProtocol.connectionLost(self, reason)
	
	def sendRequest(self, strings):
		"""sends something to the other end, returns a Deferred"""
		### TODO: this needs to add items to a cache so we can fire the deferred later
		###       we should probably also track command rtt
		cb = Deferred()
		seq = self.peekSeq()
		self.callbacks[seq] = cb
		self.transport.write(self.EncodeClientRequest(strings))
		return cb
	
	def gotResponse(self, packet):
		"""handles incoming response packets"""
		if packet.sequence in self.callbacks:
			self.callbacks[packet.sequence].callback(packet.words)
			del self.callbacks[packet.sequence]
		else:
			print "gotResponse WITHOUT callback"
	
	def sendResponse(self, pkt, words=["OK"]):
		"""called by gotRequest to send a response"""
		self.transport.write(self.EncodeServerResponse(pkt.sequence, words))
	
	def gotRequest(self, packet):
		"""handles incoming request packets
		   in client mode, these are events
		"""
		handler = None
		command = packet.words[0]
		if command in self.handlers:
			handler = self.handlers[command]
			try:
				handler(packet)
			except Exception, E:
				print "Caught Exception in gotRequest:",E
		else:
			print "Unhandled event:",packet
		self.sendResponse(packet)
