import logging
from fnmatch import fnmatch
from txmongo.dbref import DBRef
from twisted.internet import defer
from datetime import datetime
from utils.roundtime import roundTime

log = logging.getLogger("stats")

@defer.inlineCallbacks
def inlinecommand_stats(bot, user, channel, args):
	reply = bot.replyto(user, channel)
	nick  = bot.factory.getNick(user)
	mongo = bot.network.data["mongo"] # shortcut
	st    = bot.network.data["root"].getStats()

	if not len(args):
		bot.say(reply, "\x02stats\x02: usage: !stats <name>")
		defer.succeed(None)
		return
	
	if st == None:
		defer.succeed(None)
		return
	
	stats = yield st.getStats(args)
	if stats == None:
		bot.say(reply, "\x02stats\x02: %s not found" % args)
	else:
		if stats['seen'] != None:
			_dd = roundTime(datetime.now()) - roundTime(stats['seen'])
			stats['seen'] = " | Last seen: " + str(_dd) + ' ago'
		else:
			stats['seen'] = ''
		if stats['clanTag'] != '':
			stats['clanTag'] = "[%(clanTag)s] " % stats
		bot.say(reply, str("\x02stats\x02: %(clanTag)s%(personaName)s: Rank: %(rank)u | Score: %(score)u | Skill: %(skill)u | SPM: %(scorePerMinute)u | KDR: %(kdRatio).2f | WLR: %(wlRatio).2f%(seen)s" % stats))
