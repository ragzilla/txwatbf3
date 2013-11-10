from twisted.internet import defer
from cyclone.httpclient import fetch
from simplejson import loads
from urllib import quote

class StatsProvider():
	headers = { 'X-AjaxNavigation': ['1',], 'User-Agent': ['txwatfbrcon - txwatfbrcon@evilgeni.us',], }
	root = None
	config = None

	def __init__(self, root, config):
		self.root = root
		self.config = config

	@defer.inlineCallbacks
	def getStats(self, player):
		response = yield fetch('https://battlelog.battlefield.com/bf4/user/' + quote(player) + '/', headers=self.headers)

		if response.code != 200: 
			defer.succeed(None)
			return

		# if the soldiersBox key isn't present, it's an invalid origin handle
		user = loads(response.body)['context']
		if 'soldiersBox' not in user.keys():
			defer.succeed(None)
			return

		# if a personaId isn't found with gameId 2048 they don't have a bf4 soldier
		personaId = None
		personaName = None
		clanTag = ""
		for soldier in user['soldiersBox']:
			if soldier['game'] != 2048: continue
			personaId = soldier['persona']['personaId']
			personaName = soldier['persona']['personaName']
			clanTag = soldier['persona']['clanTag']
			if clanTag == None:
				clanTag = ''
		if personaId == None:
			defer.succeed(None)
			return
		
		# ok, we have a personaId, now we can pull some stats from warsaw
		response = yield fetch('https://battlelog.battlefield.com/bf4/warsawoverviewpopulate/' + personaId + '/1/', 
								headers=self.headers)

		if response.code != 200:
			defer.succeed(None)
			return

		# if the overviewStats key isn't present, no stats are shown, backend down situation
		data = loads(response.body)['data']
		if 'overviewStats' not in data.keys():
			defer.succeed(None)
			return

		stats = data['overviewStats']

		# fix some stats
		stats['personaName'] = personaName
		stats['clanTag'] = clanTag
		stats['kdRatio'] = float(stats['kills']) / float(stats['deaths'])
		stats['wlRatio'] = float(stats['numWins']) / float(stats['numLosses'])

		defer.returnValue(stats)

