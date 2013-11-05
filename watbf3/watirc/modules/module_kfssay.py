import logging
from txmongo.dbref import DBRef
from twisted.internet import defer
from random import shuffle

log = logging.getLogger("kfssay")

@defer.inlineCallbacks
def inlinecommand_kfssay(bot, user, channel, args):
	reply = bot.replyto(user, channel)
	nick  = bot.factory.getNick(user)
	mongo = bot.network.data["mongo"] # shortcut
	rc    = bot.network.data["root"].getRcon()
	tag   = bot.network.data["tag"]
	inst  = rc.getInstance(tag)
	
	if bot.factory.isAdmin(user) and len(args) > 0:
		foo = yield inst.admin_say("irc/%s: %s" % (nick, args), "all")
	else:
		bot.say(reply, "\x02kfssay\x02: admin only, scrub.")
	
