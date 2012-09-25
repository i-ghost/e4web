import urllib, urllib2, json

def googl(request, googleapikey):
	'''
	Function to return a goo.gl adddress.
	Returns input if shortened url can't be fetched
	Example: print googl('http://google.com')
	'''
	try:
		x = urllib2.Request("https://www.googleapis.com/urlshortener/v1/url",
		headers = {'Content-Type' : 'application/json'},
		data=json.dumps({'longUrl':request,'key':googleapikey}))
		x = urllib2.urlopen(x) #open it
		x = json.load(x) #load it
		return x['id']
	except:
		return request