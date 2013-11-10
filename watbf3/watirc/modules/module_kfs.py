import logging
from txmongo.dbref import DBRef
from twisted.internet import defer
from time import time

log = logging.getLogger("lcaust")

@defer.inlineCallbacks
def inlinecommand_kfs(bot, user, channel, args):
	reply = bot.replyto(user, channel)
	mongo = bot.network.data["mongo"] # shortcut
	rc    = bot.network.data["root"].getRcon()
	tag   = bot.network.data["tag"]

	if (time() - inlinecommand_kfs.lastrun) < 30: # 30 second cooldown
		bot.say(reply, "!kfs: stop spamming !lcaust")
		defer.succeed(None)
		return
	
	inlinecommand_kfs.lastrun = time()
	
	# retval = yield rc.sendRcon(tag, ["serverInfo"])
	instance = rc.getInstance(tag)
	si = yield instance.serverInfo()
	pl = yield instance.admin_listPlayers()
	plist = []
	for player in pl:
		plist.append(str(player).lower())
	goons = yield mongo.bf3names.find({"$and": [
					{"bf3state": {"$ne": 0}},
					{"bf3name": {"$in": plist}}
					]}, fields=['bf3name','bf3state',])
	si['numGoons'] = len(goons)
	if si['curPlayers'] > 0:
		si['goonPct']  = (float(si['numGoons'])/float(si['curPlayers']))*100
	else:
		si['goonPct']  = 0

	output = "\x02%(serverName)s\x02 (%(curPlayers)u/%(maxPlayers)u) [%(numGoons)u goons - %(goonPct)u%%]" % si
	bot.say(reply, str(output))
	
	output = "%(level)s (%(mode)s) [Round %(roundsPlayed)u/%(roundsTotal)u]" % si
	teamoutput = []
	for team in si['teams']:
		teamoutput.append("%(faction)s: %(score)u" % team)
	si['teamoutput'] = ' / '.join(teamoutput)
	output = "%(level)s (%(mode)s) [Round %(roundsPlayed)u/%(roundsTotal)u] %(teamoutput)s" % si

	bot.say(reply, str(output))

	if len(goons) > 10:
		bot.say(reply, "Goons: too many to list")
		return

	buf = "Goons: "
	for goon in goons:
		name = goon['bf3name']
		if len(buf) + 2 + len(name) > 140:
			# flush buffer, start over
			bot.say(reply, str(buf[:-2]))
			buf = "Goons: "
		buf += name + ", "
	if len(buf) and buf != "Goons: ":
		bot.say(reply, str(buf[:-2]))

inlinecommand_kfs.lastrun = 0.0
