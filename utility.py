import datetime 
import sys
import urllib2
import md5
from app_settings import *

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
def get_now():
	return datetime.datetime.now() + datetime.timedelta(hours=9)

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
	return md5(str(string)).hexdigest()

def jst_date(value):
    if not value:
        value = datetime.datetime.now()

    value = value.replace(tzinfo=UtcTzinfo()).astimezone(JstTzinfo())
    return value