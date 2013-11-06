import logging
from fnmatch import fnmatch
from txmongo.dbref import DBRef
from twisted.internet import defer

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
	bot.say(reply, "\x02stats\x02: %(personaName)s: Rank: %(rank)u | Score: %(score)u | Skill: %(skill)u | SPM: %(scorePerMinute)u | KDR: %(kdRatio).2f | WLR: %(wlRatio).2f" % stats)
