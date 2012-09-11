"""
Reload module
"""
import os

def command(ircbot, mask, args):
	"""Reloads modules; specify '*' as the first argument to reload all modules
If the module is not already loaded, it is loaded and removed from the runtime blacklist
Usage: %PREFIXreload module1 module2"""
	if len(args) == 1 and args[0] == u"*":
		ircbot.load_modules()
	else:
		for arg in args:
			if arg not in ircbot.modules:
				try:
					print("Attempting to load new module: %s") % (arg)
					p = os.path.join(os.getcwd(), ircbot.modulesdir, (os.path.basename("%s.py") % (arg)))
					ircbot._import_module(arg, p)
				except Exception, e:
					print("Couldn't load module '%s': %s") % (arg, e)
					return
			elif arg == ircbot.modules[arg].__origname__: # Prevent reloading by alias as it causes problems /
				p = ircbot.modules[arg].__file__	# (alias function references are updated, but original one isn't)
				ircbot._import_module(arg, p)
			else:
				print("Reloading by alias is not allowed (%s)") % (arg)