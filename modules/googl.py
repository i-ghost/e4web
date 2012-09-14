"""
Function to return a goo.gl adddress.
"""

import urllib2
import json

def command(ircbot, source, nick, mask, args):
	"""Takes a space-separated list of websites and returns their shortened goo.gl form / Usage: %PREFIX%BOLDgoogl%RESET http://foo.com http://bar.com"""
	if not args:
		ircbot.msg(nick, command.__doc__, notice=True) # return the docstring to the user if there are no arguments
		return
	result = []
	headers = {'Content-Type' : 'application/json'}
	for site in args:
		try:
			data=json.dumps({'longUrl':site,'key':ircbot.config.googleapikey})
			x = urllib2.Request("https://www.googleapis.com/urlshortener/v1/url", headers=headers, data=data)
			x = urllib2.urlopen(x) #open it
			x = json.load(x) #load it
			result.append(x['id'])
		except Exception, e:
			print e
	ircbot.msg(source, " ".join(result))
		
aliases = ["google", "g"]