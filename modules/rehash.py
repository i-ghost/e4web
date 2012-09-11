"""
Example
"""

def command(ircbot, mask, args):
	"""Usage: %PREFIXrehash"""
	if mask == ircbot.config.owner:
		ircbot.load_config()
		print("Configuration reloaded: %s") % (mask)
	else:
		print("Unauthorised")