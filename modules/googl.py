"""
Function to return a goo.gl adddress.
"""

import urllib2
import json
from modules.moduledeps import googl

def command(ircbot, source, nick, mask, args):
	"""Takes a space-separated list of websites and returns their shortened goo.gl form / Usage: %PREFIX%BOLDgoogl%RESET http://foo.com http://bar.com"""
	if not args:
		ircbot.msg(nick, command.__doc__, notice=True) # return the docstring to the user if there are no arguments
		return
	result = []
	headers = {'Content-Type' : 'application/json'}
	for site in args:
		try:
			result.append(googl.googl(site, ircbot.config.googleapikey))
		except Exception, e:
			print e
	ircbot.msg(source, " ".join(result))
		
aliases = ["google", "g"]