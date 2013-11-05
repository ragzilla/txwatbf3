"""
module_nickserv.py
this module handles automatic nickserv identification
"""

import logging

log = logging.getLogger("nickserv")
	
def handle_noticed(bot, user, channel, message):
	if user == bot.network.data['services.user'] and channel == bot.nickname: # this is a chanserv notice
		if message.startswith("This nickname is registered and protected."):
			bot.say("NickServ", "IDENTIFY %s" % bot.network.data['services.password'])
			bot.mode(bot.nickname, '-', 'x') # unhide ident
			log.info("NickServ is asking me to identify...")
		elif message.startswith("Password accepted - you are now recognized."):
			log.info("Successfully identified with NickServ")