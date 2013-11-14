import logging
from txmongo.dbref import DBRef
from twisted.internet import defer
from random import shuffle
from time import time

log = logging.getLogger("lcaust")

@defer.inlineCallbacks
def inlinecommand_lcaust(bot, user, channel, args):
	reply = bot.replyto(user, channel)
	mongo = bot.network.data["mongo"] # shortcut
	rc    = bot.network.data["root"].getRcon()
	tw    = bot.network.data["root"].getTwitter()
	tag   = bot.network.data["tag"]
	inst  = rc.getInstance(tag)

	if not bot.factory.isAdmin(user) and (time() - inlinecommand_lcaust.lastrun) < 60: # 60 second cooldown
		bot.say(reply, "!lcaust: stop spamming !lcaust")
		defer.succeed(None)
		return
	
	inlinecommand_lcaust.lastrun = time()
	
	#retval = yield rc.sendRcon(tag, ["version"])
	#print retval
	players = yield inst.admin_listPlayers()
	plist   = []
	exempt  = []
	for player in players:
		plist.append(str(player).lower())
	goons   = yield mongo.bf3names.find({"$and": [
						{"bf3state": {"$ne": 0}},
						{"bf3name": {"$in": plist}}
						]}, fields=['bf3name','bf3state',])
	for goon in goons:
		exempt.append(goon['bf3name'])
	# print exempt
	numKicks = len(players) - 60
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

		if tw:
			tw.update_status(status='Sorry ' + ', '.join(kicked) + ' #kfsbf4')
	else:
		bot.say(reply, "!lcaust: Not enough slots in use.")

inlinecommand_lcaust.lastrun = 0.0
