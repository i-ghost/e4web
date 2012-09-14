"""
An example module demonstrating basic access control, aliasing, listening, and documentation substitution.
"""

def command(ircbot, source, nick, mask, args):
	"""Usage: %PREFIX%BOLDexample%RESET"""
	if mask in ircbot.config.trusted:
		result = u"Success: %s %s" % (mask, " ".join(args))
	else:
		result = u"Unauthorised"
	ircbot.msg(source, result, notice=True)
	
def listen(ircbot, source, nick, mask, args):
	"""Define a listen function to listen to incoming public and private messages"""
	ircbot.msg(source, u"I heard you, %s!" % (nick))
		
def setup():
	# Define any additional setup the module requires here
	pass
		
aliases = [u"ex", u"eg"]
# Don't document aliases here in the __doc__, they are added to the function's __doc__ automatically at runtime