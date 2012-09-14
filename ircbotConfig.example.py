#/usr/bin/env python
# -*- coding: utf-8 -*-

owner = u"" # nick!user@host
trusted = [owner]
googleapikey = u""
pastebinapikey = u""
blacklist = [u"example"]
whitelist = [u"reload", u"rehash", u"unload"]
username = u"Foo"
nick = username
password = u""
channels = [(u"#channel", u"key")]
network = u""
msginterval = 0.1 # how long to wait before sending a queued message
dispatchstepreset = 5 # reset the msginterval every n messages