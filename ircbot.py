#!/usr/bin/env python
# -*- coding: utf-8 -*-

import imp, os
from irclib import IRC as irc

class IRCBot(irc):
	def __init__(self, prefix=u":", configfile=u"ircbotConfig", modulesdir=u"modules"):
		irc.__init__(self)
		self.prefix = prefix
		self.configfile = configfile
		self.modulesdir = modulesdir
		self.load_config()
		self.load_modules()
		
	def _import_module(self, name, file):
		"""Internal: Load a module and bind it to an entry in the modules dictionary"""
		if name in self.modules:
			del self.modules[name]
		try:
			m = imp.load_source(name, file)
			for n, o in vars(m).iteritems():
				if n == u"command":
					if not m.command.__doc__:
						m.command.__doc__ = u"No help is available for this command."
					else:
						m.command.__doc__ = m.command.__doc__.replace("%PREFIX", self.prefix)
					if hasattr(m, u"aliases"): # if we have aliases, bind them
						m.command.__doc__ += u"\nAliases: %s" % (", ".join(m.aliases)) # add aliases to documentation
						for alias in m.aliases:
							self.modules[alias] = m.command
						_aliases = m.aliases
					else:
						_aliases = []
					m.command.__file__ = file # make sure we can find it again.
					m.command.__origname__ = name
					m.command.__aliases__ = _aliases
					self.modules[name] = m.command
					if name in self.config.blacklist:
						self.config.blacklist.remove(name) # the user loaded this manually, se we remove it from the blacklist so it is reloaded /
					print(u"Registered: %s / Aliases: %s") % (name, u", ".join(_aliases)) # when load_modules is called next time
		except Exception, e:
			print(u"Couldn't load module '%s': %s") % (name, e)		
			
	def load_modules(self):
		"""Load all modules, sans those defined in the blacklist in the constructor"""
		self.modules = {}
		for file in os.listdir(self.modulesdir):
			if not file.startswith(u"_") and file.endswith(u".py"):
				name = file[:-3]
				file = os.path.join(os.getcwd(), self.modulesdir, (os.path.basename(file))) # create an abs path to the file
				if name not in self.config.blacklist:
					self._import_module(name, file)
				
	def load_config(self):
		"""Load the configuration file"""
		self.config = None
		self.config = imp.load_source(self.configfile, os.path.join(os.getcwd(), u"", "%s.py" % (self.configfile)))
		print("Nick: TODO / Owner: %s / Trusted: %s") % (self.config.owner, self.config.trusted)
		
	def run_debug(self):
		"""A REPL used for testing"""
		try:
			while True:
				print("%s\%s") % (self.config.blacklist, self.modules)
				inputLine = raw_input(u"\nEnter command: ")
				if inputLine.startswith(self.prefix) and not inputLine == self.prefix:
					inputLineCommand, inputLineArgs = inputLine.split(self.prefix, 1)[1].split()[0].lower(), inputLine.split(self.prefix, 1)[1].split()[1:]
					print(u"Command received: %s / Args: %s") % (inputLineCommand, inputLineArgs)
					if inputLineCommand in self.modules:
						if not inputLineArgs:
							print(self.modules[inputLineCommand].__doc__)
						else:
							#try:
							self.modules[inputLineCommand](self, u"pdpc/supporter/active/i-ghost", inputLineArgs)
							#except Exception, e:
							#	print(u"Error in module '%s': %s") % (inputLineCommand, e)
				else:
					# Just print it
					print(u"Input was: %s") % (inputLine)
		except KeyboardInterrupt:
			print(u"\nExiting...")

if __name__ == u"__main__":
	Bot = IRCBot()
	Bot.run_debug()