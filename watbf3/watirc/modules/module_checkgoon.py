import logging
from txmongo.dbref import DBRef
from twisted.internet import defer

log = logging.getLogger("checkgoon")

@defer.inlineCallbacks
def inlinecommand_checkgoon(bot, user, channel, args):
	reply = bot.replyto(user, channel)
	mongo = bot.network.data["mongo"] # shortcut
	if len(args) == 0:
		bot.say(reply, "Usage: .checkgoon <name>")
		return
	name = normalize(args)
	res  = yield mongo.bf3names.find({"bf3name": name})
	if res == []: # blank document, no bf3name match
		saf = yield mongo.safnames.find_one({"safname": name})
		if saf != {}:
			res = yield mongo.bf3names.find({"safname": DBRef(mongo.safnames, saf["_id"])})
		else:
			bot.say(reply, "No match found")
			return
	ref   = res[0]['safname']
	owner = yield mongo[ref.collection].find_one(ref.id)
	names = []
	for bf3name in res:
		names.append(bf3name['bf3name'])
	output = "\x02checkgoon: %s:\x02 %s" % (owner['safname'], ", ".join(names))	
	bot.say(reply, str(output))
	
def normalize(str):
	return str.lower()
