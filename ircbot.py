#!/usr/bin/env python
# -*- coding: utf-8 -*-

import imp, os, irclib, time
from irclib import IRC as irc
from collections import deque
"""
TODO:
* Write event handlers.
* Maybe make configuration loading use ConfigParser instead of just loading it as a module, would allow writing any changes made during runtime.
* More docstring substitution options.
"""

class IRCBot(irc):
	def __init__(self, prefix=u":", configfile=u"ircbotConfig", modulesdir=u"modules"):
		irc.__init__(self)
		self.prefix = prefix
		self.configfile = configfile
		self.modulesdir = modulesdir
		self.server = self.server()
		self.load_config()
		self.load_modules()
		self.core = {}
		self.listeners = {}
		self._bind_core_commands()
		# Message queue stuff
		self.msgq = deque([])
		self.msginterval = self.config.msginterval or 0.25
		self._msginterval = self.config.msginterval or 0.25
		self.dispatchstep = 0
		self.dispatchstepreset = self.config.dispatchstepreset or 5
		
	def _bind_core_commands(self):
		# The following comands are defined here and bound to a core dict rather than as reloadable modules as there's no point in them ever being /
		# un/reloaded during runtime; they have very fixed functionality.
		# In any case these can be 'overridden' by specifying a module plugin with the same name; the bot looks in the modules dict first.
		self.bind_core("reload", self.core_reload, aliases=[u"load"])
		self.bind_core("join", self.core_join, aliases=[u"j"])
		self.bind_core("part", self.core_part, aliases=[u"p"])
		self.bind_core("action", self.core_ctcp_action, aliases=[u"me"])
		self.bind_core("quit", self.core_quit, aliases=[u"die"])
		self.bind_core("msg", self.core_msg, aliases=[u"say"])
		self.bind_core("help", self.core_help)
		self.bind_core("unload", self.core_unload)
		self.bind_core("rehash", self.core_rehash)
		self.bind_core("nick", self.core_nick)
			
	def _import_module(self, name, file):
		"""Internal: Load a module command using imp and set it up"""
		try:
			module = imp.load_source(name, file) # load the module
			for n, o in vars(module).iteritems():
				if n == u"command":
					if not module.command.__doc__:
						module.command.__doc__ = u"No help is available for this command." # Default docstring
					else:
						module.command.__doc__ = self._doc_substitute(module.command.__doc__)
					if hasattr(module, u"aliases"):
						module.command.__doc__ += u" / Aliases: %s" % (", ".join(module.aliases)) # add aliases to documentation
					self.bind(name, module) # bind it to the name
					if name in self.config.blacklist:
						self.config.blacklist.remove(name) # the user loaded this manually, se we remove it from the blacklist so it is reloaded when load_modules is called next time
				elif n == u"setup":
					try:
						module.setup() # run the plugin's setup if it has one
					except Exception, e:
						return u"Error in '%s'.setup(): %s" % (name, e)
				elif n == u"listen":
					print(u"Added global handler for module: '%s'") % (name)
					self.modules[name].command.__doc__ += u" / This module listens for input"
					self.listeners[name] = (module.listen)

		except Exception, e:
			return u"Couldn't load '%s': %s" % (name, e)
		else:
			return name
	
	def bind(self, name, module):
		"""Bind a module to a name and its aliases (if any)"""
		if name in self.modules:
			del self.modules[name]
		self.modules[name] = module
		if hasattr(module, u"aliases"):
			for alias in module.aliases:
				if alias in self.modules:
					del self.modules[alias]
				self.modules[alias] = module
		else:
			module.aliases = []
		print(u"Bound: %s / Aliases: %s") % (name, u", ".join(module.aliases))
			
	def load_modules(self):
		"""Load all modules, sans those defined in the blacklist in the config"""
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
		print("Nick: %s / Owner: %s / Trusted: %s") % (self.config.nick, self.config.owner, self.config.trusted)
		
	def _doc_substitute(self, doc):
		"""Internal: Substitutes tokens in a docstring"""
		replacements = {u"%PREFIX": self.prefix, u"%BOLD": u"", u"%RESET": u""}
		for i in replacements:
			if i in doc:
				doc = doc.replace(i, replacements[i])
		return doc
		
	def bind_core(self, name, command, aliases=[]):
		"""Bind a core command to a name and its aliases (if any)"""
		if name in self.core:
			del self.core[name]
		command.__func__.__doc__ = self._doc_substitute(command.__func__.__doc__)
		self.core[name] = command
		if aliases:
			command.__func__.aliases = aliases
			command.__func__.__doc__ += u" / Aliases: %s" % (", ".join(aliases)) # add aliases to documentation
			for alias in aliases:
				if alias in self.core:
					del self.core[alias]
				self.core[alias] = command
		print(u"Bound core: %s / Aliases: %s") % (name, u", ".join(aliases))
		
	def core_reload(self, source, nick, mask, args):
		"""Loads/reloads modules; specify '*' as the first argument to reload all modules. If the module is not already loaded, it is loaded and removed from the runtime blacklist / Usage: %PREFIX%BOLDreload%RESET module1 module2"""
		if not args:
			self.msg(source, self.core_reload.__doc__, notice=True)
			return
		if len(args) == 1 and args[0] == u"*":
			self.load_modules()
			self.server.privmsg(source, u"Reloaded all modules")
		else:
			result = []
			for arg in args:
				if arg not in self.modules:
					p = os.path.join(os.getcwd(), self.modulesdir, (os.path.basename("%s.py") % (arg)))
					if os.path.exists(p):
						result.append(u"New module: %s" % (self._import_module(arg, p)))
				elif arg in self.modules:
					p = self.modules[arg].__file__
					self._import_module(arg, p)
					result.append(u"Reloaded: '%s'" % (arg))
				elif arg in self.modules[arg].aliases: # Prevent reloading by alias as it causes problems (function references are updated, but original one isn't)
					result.append(u"Reloading by alias is not allowed (%s)" % (arg))
			self.msg(source, u" / ".join(result))
			
	def core_unload(self, source, nick, mask, args):
		"""Unloads modules; specify '*' as the first argument to unload all modules. Unloaded modules are added to the blacklist. Modules defined in the config whitelist are never unloaded. / Usage: %PREFIX%BOLDunload%RESET module1 module2"""
		if not args:
			self.msg(source, self.core_reload.__doc__, notice=True)
			return
		if len(args) == 1 and args[0] == u"*":
			# remove all commands and their aliases, sans whitelisted
			for k in self.modules.keys():
				if k in self.config.whitelist: continue;
				_aliases = self.modules[k].aliases
				del self.modules[k]
				if k in _aliases: continue;
				self.blacklist.append(k)
		else:
			result = []
			for arg in args:
				try:
					if arg in self.modules[arg].aliases:
						result.append(u"Unloading by alias is not allowed (%s)" % (arg))
				except KeyError:
					if arg not in self.core:
						result.append(u"No module named '%s'" % (arg))
				if arg in self.modules:
					if arg in self.config.whitelist:
						result.append(u"Can't unload '%s': protected command" % (arg))
						continue
					result.append(u"Unloading: %s" % (arg))
					if self.modules[arg].aliases:
						for alias in self.modules[arg].aliases:
							del self.modules[alias]
					del self.modules[arg]
					if arg in self.listeners:
						del self.listeners[arg]
				if arg in self.core:
					result.append(U"'%s' is a core command and can't be unloaded" % (arg))
		self.msg(source, " / ".join(result))
		
	def core_rehash(self, source, nick, mask, args):
		"""Usage: %PREFIX%BOLDrehash%RESET"""
		if mask == self.config.owner:
			self.load_config()
			self.msg(source, u"Configuration reloaded.")
		else:
			self.msg(source, u"Unauthorised.")
		
	def core_join(self, source, nick, mask, args):
		"""Join channels / Usage: %PREFIX%BOLDjoin%RESET chan1<:key> chan2 chan3<:key> ..."""
		if not args:
			self.msg(source, self.core_join.__doc__, notice=True)
			return
		for arg in args:
			try:
				chan, key = arg.partition(u":")[0], arg.partition(u":")[2]
				self.server.join(chan, key=key)
			except:
				self.server.join(chan)
				
	def core_part(self, source, nick, mask, args): # FIXME: doesn't seem to work ?
		"""Part channels / Usage %PREFIX%BOLDpart%RESET chan1<:reason> chan2 chan3<:reason> ..."""
		for arg in args:
			try:
				chan, reason = arg.partition(u":")[0], arg.partition(u":")[2]
				self.server.part(chan, message=reason)
			except Exception, e:
				print e
				self.server.part(arg, message=u"Parting from %s" % (arg))
			print arg
				
	def core_quit(self, source, nick, mask, args):
		"""Send a quit message to the server / Usage %PREFIX%BOLDquit%RESET <message>"""
		message = u"Received instruction to quit."
		if args:
			message = u" ".join(args)
		self.server.quit(message=message)
		self.server.disconnect()
		
	def core_ctcp_action(self, source, nick, mask, args):
		"""Sends a CTCP ACTION to a target / Usage %PREFIX%BOLDaction%RESET <target:>action"""
		args = u" ".join(args).partition(u":")
		if args[1] == u":":
			target, action = args[0], args[2]
		else:
			target, action = source, args[0]
		if not action:
			self.msg(source, self.core_ctcp_action.__doc__)
		else:
			self.server.action(target, action)
		print u"Target:%s / Action: %s" % (target, action)
		
	def core_msg(self, source, nick, mask, args):
		"""Sends a message as the bot to a target / Usage %PREFIX%BOLDmsg%RESET <target:>message"""
		args = u" ".join(args).partition(u":")
		if args[1] == u":":
			target, message = args[0], args[2]
		else:
			target, message = source, args[0]
		if not message:
			self.msg(source, self.core_msg.__doc__)
		else:
			self.msg(target, message)
		print u"Target:%s / Action: %s" % (target, message)
		
	def core_nick(self, source, nick, mask, args):
		"""Change the bot's nick / Usage %PREFIX%BOLDnick%RESET new_nick""" # FIXME: isn't picked up by help
		newnick = args[0]
		self.server.nick(newnick)
		
	def core_help(self, source, nick, mask, args):
		"""Gives help about a specific command / Usage %PREFIX%BOLDhelp%RESET command"""
		if not args:
			topics = [u"%BOLDhelp%RESET"] # FIXME: help doesn't seem to be included for some reason
			for k in self.modules:
				try:
					if k not in self.modules[k].aliases:
						topics.append(u"%BOLD" + k + u"%RESET")
				except:
					pass
			for k in self.core:
				try:
					if k not in self.core[k].aliases:
						topics.append(u"%BOLD" + k + u"%RESET")
				except:
					pass
			message = self._doc_substitute(u"Available commands: %s " % (", ".join(topics)) +u"/ Type %PREFIX%BOLDhelp%RESET command for help with a specific command")
			self.msg(source, message)
		elif args[0] in self.modules:
			self.msg(nick, self.modules[args[0]].command.__doc__, notice=True)
		elif args[0] in self.core:
			self.msg(nick, self.core[args[0]].command.__doc__, notice=True)
		else:
			self.msg(nick, u"Unrecognised command: '%s', use %shelp for a list of available commands" % (args[0], self.prefix), notice=True)

	def load_handlers(self, conn, event):
		"""TODO: Bind the irclib handlers"""
		pass
		
	def msg(self, target, message, notice=False):
		"""Loads a message into the queue for sending"""
		if self.msginterval <= 0:
			print(u"--We should never see this--")
			self.msginterval = 0
		if len(message) > 500: # max is 512, but 500 is a good round number to account for control codes, CR/LF etc.
			self.msgq.append((target, message[:500], notice))
			self.msgq.append((target, message[500:], notice))
		else:
			self.msgq.append((target, message, notice))
		self.msginterval += self._msginterval
		
	def dispatch(self):
		"""Dispatch a message""" # TODO: thread this
		time.sleep(self.msginterval)
		if self.msgq:
			msg = self.msgq.popleft()
			if msg[2]:
				self.server.notice(msg[0], msg[1])
			else:
				self.server.privmsg(msg[0], msg[1])
			self.dispatchstep += 1
			if self.dispatchstep >= self.config.dispatchstepreset:
				self.msginterval = self.config.msginterval # every n messages dispatched, reset the msginterval
				self.dispatchstep = 0
		
		
				
	def listen_forever(self):
		"""Listen forever and call the message dispatcher"""
		while self.server.connected:
			self.process_once(0.2)
			self.dispatch()

	def run_debug(self):
		"""A REPL used for testing"""
		try:
			while True:
				print("%s\n%s\n%s") % (self.config.blacklist, self.modules, self.core)
				inputLine = [raw_input(u"\nEnter command: ")][0]
				if inputLine.startswith(self.prefix) and not inputLine == self.prefix:
					inputLineCommand, inputLineArgs = inputLine.split(self.prefix, 1)[1].split()[0].lower(), inputLine.split(self.prefix, 1)[1].split()[1:]
					print(u"Command received: %s / Args: %s") % (inputLineCommand, inputLineArgs)
					if inputLineCommand in self.modules:
						if not inputLineArgs:
							print(self.modules[inputLineCommand].command.__doc__)
						else:
							print(self.modules[inputLineCommand].command(self, u"REPL", "i-ghost", u"pdpc/supporter/active/i-ghost", inputLineArgs))
					elif inputLineCommand in self.core:
						if not inputLineArgs:
							print(self.core[inputLineCommand].__doc__)
						else:
							print(self.core[inputLineCommand](u"REPL", "i-ghost", u"pdpc/supporter/active/i-ghost", inputLineArgs))
				else:
					# Just print it
					print(u"Input was: %s") % (inputLine)
		except KeyboardInterrupt:
			print(u"\nExiting...")
			
	def message_handler(self, connection, event):
		"""Handle all incoming messages"""
		message = event.arguments()[0] # irclib gives us a list of length 1 for some reason
		mask = event.source()
		nick = irclib.nm_to_n(mask)
		if event.target() == self.server.get_nickname(): # It's a private (query) message /
			source = irclib.nm_to_n(event.source()) # so return to sender
		else:
			source = event.target() # message was sent to a channel
		if message.startswith(self.prefix) and not message == self.prefix:
			module, args = message.split(self.prefix, 1)[1].split()[0].lower(), message.split(self.prefix, 1)[1].split()[1:]
			print(u"%s received: %s / Args: %s / Sender: %s / Target: %s") % (event.eventtype(), module, args, event.source(), event.target())
			if module in self.modules:
				try:
					self.modules[module].command(self, source, nick, mask, args)
				except Exception, e:
					print(u"%s: ") % (e)
			elif module in self.core and mask in self.config.trusted:
				try:
					self.core[module](source, nick, mask, args)
				except Exception, e:
					print(u"%s: ") % (e)
			else:
				if irclib.is_channel(event.target()):
					self.server.privmsg(event.target(), u"Unrecognised command")
				else:
					self.server.privmsg(irclib.nm_to_n(event.source()), u"Unrecognised command")
		for listener in self.listeners: # TODO: thread this
			self.listeners[listener](self, source, nick, mask, message)
			
	def connect(self):
		self.add_global_handler(u"pubmsg", self.message_handler)
		self.add_global_handler(u"privmsg", self.message_handler)
		self.server.connect(self.config.network, 6697, nickname=self.config.nick, username=self.config.username, ircname=self.config.nick, ssl=True, password=self.config.password or u"")
		for chan, key in self.config.channels:
			self.server.join(chan, key=key)
		try:
			self.listen_forever()
		except KeyboardInterrupt:
			self.server.disconnect()

if __name__ == u"__main__":
	Bot = IRCBot()
	Bot.connect()