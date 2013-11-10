from datetime import datetime, timedelta
from copy import deepcopy
from threading import RLock
from twisted.internet import defer

def timedCache(seconds=0, minutes=0, hours=0, days=0):

	time_delta = timedelta( seconds=seconds,
							minutes=minutes,
							hours=hours,
							days=days )

	def decorate(f):

		f._lock = RLock()
		f._updates = {}
		f._results = {}

		@defer.inlineCallbacks
		def do_cache(*args, **kwargs):

			lock = f._lock
			lock.acquire()

			try:
				key = (args, tuple(sorted(kwargs.items(), key=lambda i:i[0])))

				updates = f._updates
				results = f._results

				t = datetime.now()
				updated = updates.get(key, t)

				if key not in results or t-updated > time_delta:
					# Calculate
					updates[key] = t
					result = yield f(*args, **kwargs)
					results[key] = deepcopy(result)
					defer.returnValue(result)
					defer.succeed()
					return

				else:
					# Cache
					defer.returnValue(deepcopy(results[key]))
					defer.succeed()
					return

			finally:
				lock.release()

		return do_cache

	return decorate
