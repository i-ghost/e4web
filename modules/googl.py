'''
Function to return a goo.gl adddress.
'''

import urllib2
import json

def command(ircbot, mask, args):
	"""Takes a space-separated list of websites and returns their shortened goo.gl form
Usage: %PREFIXgoogl http://foo.com http://bar.com
"""
	result = []
	for site in args:
		try:
			x = urllib2.Request("https://www.googleapis.com/urlshortener/v1/url",
			headers = {'Content-Type' : 'application/json'},
			data=json.dumps({'longUrl':site,'key':ircbot.config.googleapikey}))
			x = urllib2.urlopen(x) #open it
			x = json.load(x) #load it
			
			result.append(x['id'])
		except:
			pass
	print result
		
aliases = ["google", "g"]