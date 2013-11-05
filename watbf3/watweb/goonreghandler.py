from basehandler import BaseHandler
from cyclone.httpclient import fetch
from urllib import quote_plus
from twisted.internet import defer
from BeautifulSoup import BeautifulSoup
from txmongo.dbref import DBRef
import base64
import os

class GoonregHandler(BaseHandler):
	def get(self):
		if 'challenge' not in self.session.keys():
			self.session['challenge'] = base64.b32encode(os.urandom(10))
		e = self.get_argument("e", None)
		errormsg=(e == "invalid" and "<br/>Invalid SA Forums name, or missing challenge in 'Interests' field." or "")
		self.render("goonreg-get.html", errormsg=errormsg, challenge=self.session['challenge'])
	
	@defer.inlineCallbacks
	def post(self):
		if 'challenge' not in self.session.keys():
			self.redirect("/goonreg?e=invalid")
			return
		challenge = self.session['challenge']
		# del self.session['challenge'] ### TODO: commented for testing

		# let's pull ourselves a profile!
		saf, bf3 = self.get_argument("saf", None).lower(), self.get_argument("bf3", None).lower()
		if not saf or not bf3:
			self.redirect("/goonreg?e=invalid")
			return
		
		profileurl = "http://forums.somethingawful.com/member.php?s=&action=getinfo&username=%s" % quote_plus(saf)
		profile = yield fetch(profileurl, 
			headers={'Cookie': ['bbuserid=x;bbpassword=x']})
		# BeautifulSoup doesn't care much about good markup, it just gets the job done.
		soup = BeautifulSoup(profile.body)
		if str(soup.find('title')) == '<title>The Something Awful Forums</title>':
			self.redirect("/goonreg?e=invalid")
			return
		# found a good profile, now to check interests
		interests = soup.find('dt', text='Interests')
		if not interests:
			# no interests block found
			self.redirect("/goonreg?e=invalid")
			return
		challenger = interests.next.text
		if not challenger:
			self.redirect("/goonreg?e=invalid")
			return
		if challenger.find(challenge) == -1:
			# challenge not found
			self.redirect("/goonreg?e=invalid")
			return
		# found the challenger! it exploded!
		# process the goon registration
		watbf3 = self.settings.mongo.watbf3 # shortcut
		safentry = yield watbf3.safnames.find_one({"safname": saf})
		bf3state = 1 # bf3state determines if this is the first nick, or if it has any additional privileges (0 == secondary nick, 1 == primary)
		if safentry == {}: # if it's an empty dict, ie no doc found, insert a new primary record
			safhandle = yield watbf3.safnames.insert( {"safname": saf, "reglimit": 5} )
			print "yielded new safhandle:",safhandle
			bf3state = 2
		else:
			safhandle = safentry['_id']
			count = yield watbf3.bf3names.count({"safname": DBRef(watbf3.safnames, safhandle)})
			count = int(count)
			reglimit = int(safentry["reglimit"])
			if count >= reglimit:
				self.render("goonreg-error.html", error="You have exceeded your allowed registrations (%u/%u)" % (count,reglimit), bf3=bf3)
				return
		# insert a new bf3names entry
		try:
			# normalize the bf3 name
			# bf3 = str(bf3).translate(None, " -_") # bfbc2 r13 conventions
			# try to find an existing bf3name
			bf3handle = yield watbf3.bf3names.find_one({"bf3name":bf3})
			if bf3handle == {}: # empty dict, nothing found
				# ok, install a new bf3name
				bf3handle = yield watbf3.bf3names.insert({
					"bf3name":  bf3,
					"safname":  DBRef(watbf3.safnames, safhandle),
					"bf3state": bf3state,
					"bf3guid":  None,
					}, safe=True)
			else:
				# update the existing
				if int(bf3handle["bf3state"]) > 0:
					self.render("goonreg-error.html", 
						error="BF3 name (%s) already registered to %s" % (bf3,saf), bf3=bf3)
					return
				bf3handle["bf3state"] = bf3state
				bf3handle["safname"]  = DBRef(watbf3.safnames, safhandle)
				watbf3.bf3names.save(bf3handle)
		except Exception as e:
			print "exception:",e
			self.render("goonreg-error.html", error="BF3 name already registered", bf3=bf3)
			return
		
		self.render("goonreg-post.html", saf=saf, bf3=bf3)

