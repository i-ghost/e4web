"""
An example module demonstrating basic access control, aliasing, and documentation substitution.
"""

def command(ircbot, mask, args):
	"""Usage: %PREFIXexample"""
	if mask in ircbot.config.trusted:
		print("Success: %s %s") % (mask, " ".join(args))
	else:
		print("Unauthorised")
		
aliases = [u"ex", u"eg"]
# Don't document aliases here in the __doc__, they are added to the function's __doc__ automatically at runtime