"""
Queries a Source server using SourceQuery
"""

from socket import gethostbyname
from modules.moduledeps import SourceQuery, googl, pasteee
from operator import itemgetter
import urllib, urllib2

def command(ircbot, source, nick, mask, args):
	"""Queries a Source engine server using the A2S protocol / Usage: %BOLD%PREFIXquery%RESET ip|hostname<:port>"""
	ip = None
	#get ip
	args = u" ".join(args).partition(u":")
	if args[1] == u":":
		ip, port = args[0], int(args[2])
	else:
		ip, port = args[0], 27015
	if not ip:
		ircbot.msg(source, command.__doc__)
		return
	try:
		ip = gethostbyname(ip)
	except:
		pass
	try:
		query = SourceQuery.SourceQuery(ip, port, 1.5)
	except:
		pass
	if not query:
		ircbot.msg(source, u"Couldn't query: %s:%d" % (ip, port))
		return
	queryInfo = query.info()
	queryRules = query.rules()
	ruleString = u""
	for rule in sorted(queryRules.iterkeys()):
		ruleString += u"%s %s\n" % (rule, queryRules[rule])
	ruleString = ruleString.rstrip(u"\n") # strip trailing newline
	# pastebin stuff
	pasteResponse = "Couldn't paste cvars"
	try:
		pasteData = pasteee.Paste(ruleString, desc="%s - cvars" % (queryInfo[u"hostname"]), key=ircbot.config.pastebinapikey)["link"]
	except PasteError, e:
		pasteResponse = e
	if pasteData:
		pasteResponse = googl.googl(pasteData, ircbot.config.googleapikey)
	tags, passworded, OS = None, None, None
	if u"tag" in queryInfo:
		tags = "Tags: %s" % (queryInfo[u"tag"])
	if queryInfo[u"passworded"]:
		passworded = "Passworded"
	if queryInfo[u"os"] == u"w":
		OS = "Windows"
	
	queryPlayersDict = sorted(query.player(), key=itemgetter(u"kills"), reverse=True)[0:3:1] or None # get the top 3 players by kills
	queryPlayersList = []
	if queryPlayersDict:
		for player in queryPlayersDict:
			queryPlayersList.append("%s:%s" % (player[u"name"], str(player[u"kills"])))
		queryPlayersList = ", ".join(queryPlayersList)
	
	message = "%s (%s) | %s | %s:%d | %d/%d - %d bots | %s | %s | %s | %s | %s | Join: steam://connect/%s:%d" % (
				"%s" % (queryInfo[u"hostname"]),
				OS or "Linux",
				"%s" % (queryInfo[u"gamedesc"]),
				ip,
				port,
				queryInfo[u"numplayers"],
				queryInfo[u"maxplayers"],
				queryInfo[u"numbots"],
				"%s" % (queryInfo[u"map"]),
				passworded or "Public",
				queryPlayersList or "No players",
				tags or "No tags",
				pasteResponse,
				ip,
				port
				)
	ircbot.msg(source, message)
