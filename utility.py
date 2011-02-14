import datetime 
import sys
import urllib2

class UtcTzinfo(datetime.tzinfo):
    def utcoffset(self, dt):
        return datetime.timedelta(0)

    def dst(self, dt):
        return datetime.timedelta(0)

    def tzname(self, dt):
        return 'UTC'

    def olsen_name(self):
        return 'UTC'

class JstTzinfo(datetime.tzinfo):
    def utcoffset(self,dt):
        return datetime.timedelta(hours=9)
    def dst(self,dt):
        return datetime.timedelta(hours=0)
    def tzname(self,dt):
        return "JST"


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
    
    
def getPhotolist(client,username):
	photolist=[]
	photos=None 
	albums = client.GetUserFeed(user=username)
	for album in albums.entry:
		photos = client.GetFeed( '/data/feed/api/user/%s/albumid/%s?kind=photo' % ( username, album.gphoto_id.text))
		for photo in photos.entry:
			photolist.append( photo.media.thumbnail[2].url )
		
	return photolist
