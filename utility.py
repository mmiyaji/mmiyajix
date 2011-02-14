import datetime 
import sys
import urllib2
import simplejson
from app_settings import *

class Googl():
	def shorten(slef,longUrl):
		if isinstance(longUrl, unicode):
			longUrl = longUrl.encode('utf-8')
	   
		if API_KEY is None:
			data = '{longUrl:"%s"}' % (longUrl)
		else:
			data = '{longUrl:"%s", key:"%s"}' % (longUrl, API_KEY)
		req = urllib2.Request(API_URL, data)
		req.add_header('Content-Type', 'application/json')
	
		result = urllib2.urlopen(req).read()
		return simplejson.loads(result).get('id')

class TinyURL:
	def get_tiny_url(self, url):
		api_url = "http://tinyurl.com/api-create.php?url="
		tiny_url = ''
		try:
			tiny_url = urllib2.urlopen(api_url + url).read()
		except urllib2.HTTPError, e:
			sys.stderr.write('%s: %s\n' % (e, url))
		except urllib2.URLError, e:
			sys.stderr.write('%s: %s\n' % (e, url))
		except:
			sys.stderr.write('Unexpected error: %s\n' % (sys.exc_info()[1]))
		return tiny_url

def jst_date(value):
    if not value:
        value = datetime.datetime.now()

    value = value.replace(tzinfo=UtcTzinfo()).astimezone(JstTzinfo())
    return value