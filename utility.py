import os,urllib,random,datetime,logging,re,urllib2,sys,md5,hashlib
import wsgiref.handlers
from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext.webapp import util
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.api import mail
from base64 import b64decode
from google.appengine.ext.webapp import template
from app_settings import *
from google.appengine.api import memcache

# FB_APP_ID="201904279853678"
# FB_API_KEY="7a493bd9213ddc2becce98930f6929ce"
# FB_SECRET="8ea45010257e0002b00e420880ab984d"
FB_APP_ID="214530545248578"
FB_API_KEY="ec49a0a98bb139153a6b8c15fd49c777"
FB_SECRET="b745e6a3d788add18779c467e587aa48"

# class Googl():
# 	def shorten(slef,longUrl):
# 		if isinstance(longUrl, unicode):
# 			longUrl = longUrl.encode('utf-8')
# 	   
# 		if API_KEY is None:
# 			data = '{longUrl:"%s"}' % (longUrl)
# 		else:
# 			data = '{longUrl:"%s", key:"%s"}' % (longUrl, API_KEY)
# 		req = urllib2.Request(API_URL, data)
# 		req.add_header('Content-Type', 'application/json')
# 	
# 		result = urllib2.urlopen(req).read()
# 		return simplejson.loads(result).get('id')

class TinyURL:
	def get_tiny_url(self,url):
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
def get_now():
	return datetime.datetime.now() + datetime.timedelta(hours=9)

def error_status(status,code=401,template_values=dict()):
	status.error(code)
	message="Sorry... "
	if code==401:
		message += "You are not authorize."
	elif code==404:
		message += "Forbidden Page."
	template_values["error_message"]=message
	path = os.path.join(os.path.dirname(__file__), './templates/base/error.html')
	status.response.out.write(template.render(path, template_values))	
	
def get_page_list(page, count, search_span):
	pages = dict()
	page_max = (count / search_span)
	if count%search_span!=0:
		page_max +=1
	pre_page = None
	next_page = None
	if page_max >= page+1:
		next_page = page+1
	if page!=0:
		pre_page = page-1
	pages['next_page'] = next_page
	pages['now_page'] = page
	pages['pre_page'] = pre_page
	pages['max'] = count
	page_list = []
	if page_max>20:
		page_list.append(1)
		mins = page-8
		maxs = page+9
		if mins<2:
			mins = 2
			maxs = 18
		# else:
			# page_list.append("-")
		if maxs>page_max:
			maxs = page_max
		for x in range(mins, maxs):
			page_list.append(x)
		# else:
		# 	for x in range(mins, maxs):
		# 		page_list.append(x)
			# page_list.append("-")
		page_list.append(page_max)
	else:
		for x in range(1, page_max+1):
			page_list.append(x)
		if len(page_list)==1:
			page_list = None
	return page_list,pages

def create_hash(string):
	return hashlib.md5(str(string)).hexdigest()

def jst_date(value):
	if not value:
		value = datetime.datetime.now()
	value = value.replace(tzinfo=UtcTzinfo()).astimezone(JstTzinfo())
	return value