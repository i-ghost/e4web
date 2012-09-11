"""
Unload
"""
import os

def command(ircbot, mask, args):
	"""Unloads modules; specify '*' as the first argument to unload all modules.
Unloaded modules are added to the blacklist. 'reload', 'rehash' and 'unload' are never unloaded.
Usage: %PREFIXunload module1 module2"""
	if len(args) == 1 and args[0] == u"*":
		for k in ircbot.modules.keys():
			if k in ircbot.config.whitelist: continue;
			_aliases = ircbot.modules[k].__aliases__
			del ircbot.modules[k]
			if k in _aliases: continue;
			ircbot.blacklist.append(k)
	else:
		for arg in args:
			try:
				if arg in ircbot.modules[arg].__aliases__:
					print("Unloading by alias is not allowed.")
			except KeyError:
				print("No module named '%s'") % (arg)
			if arg in ircbot.modules and arg == ircbot.modules[arg].__origname__:
				print("Unloading: %s") % (arg)
				if ircbot.modules[arg].__aliases__:
					for alias in ircbot.modules[arg].__aliases__:
						del ircbot.modules[alias]
				del ircbot.modules[arg]