"""
Calculates expressions using Google
"""

import urllib, urllib2

def command(ircbot, source, nick, mask, args):
	"""Calculator / Usage: %PREFIX%BOLDcalc%RESET expression / Example: %PREFIX%BOLDcalc%RESET 52+(72*65)"""
	if not args:
		ircbot.msg(nick, command.__doc__, notice=True)
		return
	args = " ".join(args)
	gcalc = urllib.urlencode({'hl':'en', 'q':args}) #encode
	gcalc = urllib2.urlopen('http://www.google.com/ig/calculator?' + gcalc) #open
	gcalc = gcalc.read().split('rhs: ')[1].split(',', 1)[0].strip('"') #read
	if gcalc:
		ircbot.msg(source, u"%s = %s" % (args, gcalc))