import logging
from fnmatch import fnmatch
from txmongo.dbref import DBRef
from twisted.internet import defer

log = logging.getLogger("kfskill")

@defer.inlineCallbacks
def inlinecommand_kfskill(bot, user, channel, args):
	reply = bot.replyto(user, channel)
	mongo = bot.network.data["mongo"] # shortcut
	rc    = bot.network.data["root"].getRcon()
	tag   = bot.network.data["tag"]
	inst  = rc.getInstance(tag)

	if not bot.factory.isAdmin(user) or len(args) == 0:
		bot.say(reply, "\x02kfskill\x02: admin only, scrub.")
		return
	
	players = yield inst.admin_listPlayers()
	plist   = []
	victims = []
	for player in players:
		plist.append(str(player).lower())

	try:
		(pattern, rest) = args.split(" ", 1)
	except ValueError as e:
		pattern = args
	pattern = pattern.lower()
	for player in plist:
		if fnmatch(player, "*%s*" % (pattern)):
			victims.append(player)
	
	if len(victims) in range(1,5):
		for victim in victims:
			inst.admin_killPlayer(victim)
		bot.say(reply, "\x02kfskill\x02: %s" % (", ".join(victims)))
	else:
		bot.say(reply, "\x02kfskill\x02: %u potential victims found." % (len(victims)))

