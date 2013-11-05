"""
$Id: module_autorejoin.py 313 2011-06-03 11:22:38Z henri@nerv.fi $
$HeadURL: http://pyfibot.googlecode.com/svn/trunk/modules/module_autorejoin.py $
"""

# rejoin after 10 seconds
delay = 10

from twisted.internet import reactor


def handle_kickedFrom(bot, channel, kicker, message):
    """Rejoin channel after 10 seconds"""
    bot.log("Kicked by %s from %s. Reason: %s" % (kicker, channel, message))
    bot.log("Rejoining in %d seconds" % delay)
    bot.network.channels.remove(channel)
    reactor.callLater(delay, bot.join, channel)
