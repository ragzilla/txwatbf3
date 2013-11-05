import logging
from txmongo.dbref import DBRef
from twisted.internet import defer
from random import shuffle

log = logging.getLogger("lcaust")

@defer.inlineCallbacks
def inlinecommand_lcaust(bot, user, channel, args):
	reply = bot.replyto(user, channel)
	mongo = bot.network.data["mongo"] # shortcut
	rc    = bot.network.data["root"].getRcon()
	tag   = bot.network.data["tag"]
	inst  = rc.getInstance(tag)
	
	#retval = yield rc.sendRcon(tag, ["version"])
	#print retval
	players = yield inst.admin_listPlayers()
	plist   = []
	exempt  = []
	for player in players:
		plist.append(str(player).lower())
	goons   = yield mongo.watbf3.bf3names.find({"$and": [
						{"bf3state": {"$ne": 0}},
						{"bf3name": {"$in": plist}}
						]}, fields=['bf3name','bf3state',])
	for goon in goons:
		exempt.append(goon['bf3name'])
	# print exempt
	numKicks = len(players) - 58
	if numKicks > 0:
		shuffle(plist)
		kicked = []
		for i in range(numKicks):
			try:
				candidate = plist.pop(0)
				while candidate in exempt:
					candidate = plist.pop(0)
			except Exception, e:
				break
			kicked.append(candidate)
		for victim in kicked:
			response = yield inst.admin_kickPlayer(victim, "freeing slots for members")

		bot.say(reply, "!lcaust: kicked: %s" % (", ".join(kicked)))
	else:
		bot.say(reply, "!lcaust: Not enough slots in use.")
