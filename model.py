# -*- coding: utf-8 -*-
from google.appengine.ext import db
from utility import *
from time import gmtime, strftime
from app_settings import *
# from filer import *
def to_dict(model_obj, attr_list, init_dict_func=None):
	values = {}
	init_dict_func(values)
	for token in attr_list:
		elems = token.split('.')
		value = getattr(model_obj, elems[0])
		for elem in elems[1:]:
			value = getattr(value, elem)
		values[elems[-1]] = value
	if model_obj.is_saved():
		values['key'] =  str(model_obj.key())
	return values

class ApplicationUser(db.Model):
	user = db.UserProperty(auto_current_user_add=True)
	role = db.StringProperty(choices=set(["admin","developper","writer", "user"]))
	nickname = db.StringProperty(default="")
	email_addr = db.StringProperty(default="")
	fullname = db.StringProperty(default="")
	img_url = db.StringProperty(default="")
	description = db.TextProperty(default="")
	create_at = db.DateTimeProperty(auto_now_add=True)
	updated_at = db.DateTimeProperty(auto_now=True)
	portfolio = db.TextProperty(default="")
	# fb_default_post_flg = db.BooleanProperty(default=False)
	fb_nickname = db.StringProperty(default="")
	fb_oauth_token = db.StringProperty(default="")
	fb_oauth_token_secret = db.StringProperty(default="")
	def is_facebook(self):
		if self.fb_oauth_token:
			return True
		else:
			return False
	def admin_auth(self):
		if self.role == "admin":
			return True
		else:
			return False
	def modify_auth(self):
		if self.role == "admin" or self.role == "developper":
			return True
		else:
			return False

	@staticmethod
	def get_by_user(user):
		return ApplicationUser.all().filter("user = ",user).get()

	@staticmethod
	def get_by_nickname(nickname):
		return ApplicationUser.all().filter("nickname = ",nickname).get()
	
	@staticmethod
	def get_users():
		return ApplicationUser.all()
	
# class Revision(db.Model):
# 	revision = db.IntegerProperty(default=0)
# 	create_appuser = db.ReferenceProperty(ApplicationUser,
# 									collection_name='commiter')
# 	create_at = db.DateTimeProperty(auto_now_add=True)
# 	updated_at = db.DateTimeProperty(auto_now_add=True)
# 	
# 	@staticmethod
# 	def get_rev(rev=0):
# 		revision = Revision.all().filter("revision = ",rev).get()
# 		return revision
# 	@staticmethod
# 	def create_revision(rev=0,appuser=None):
# 		revision = Revision()
# 		revision.revision = rev
# 		revision.create_appuser = appuser
# 		revision.put()
# 		return revision
	
class Application(db.Model):
	title = db.StringProperty(default="")
	description = db.TextProperty(default="")
	revision = db.IntegerProperty(default=0)
	img_url = db.StringProperty(default="")
	create_appuser = db.ReferenceProperty(ApplicationUser,
									collection_name='created_user')
	create_at = db.DateTimeProperty(auto_now_add=True)
	updated_at = db.DateTimeProperty(auto_now=True)
	isdefault = db.BooleanProperty(default=True)
	islock = db.BooleanProperty(default=True)
	super_user = db.StringProperty(default="")
	super_pass = db.StringProperty(default="")
	fb_flag = db.BooleanProperty(default=False)
	fb_app_id = db.StringProperty(default="")
	fb_api_key = db.StringProperty(default="")
	fb_secret = db.StringProperty(default="")
	def is_facebook(self):
		if self.fb_flag and self.fb_app_id and self.fb_api_key and self.fb_secret:
			return True
		else:
			return False
	def create_app(self,title="",rev=0,description="",appuser=None,img_url="",user="",passwd="",islock=True,
					fb_flag="",fb_app_id="",fb_api_key="",fb_secret=""):
		app = None
		if Application.all().filter("rev = ",rev).count() < 1:
			app = self
			app.title = title
			app.description = description
			app.create_appuser = appuser
			app.img_url = img_url
			app.revision = rev
			app.super_user = user
			app.super_pass = create_hash(passwd)
			app.islock = islock
			if fb_flag:
				app.fb_flag = True
			else:
				app.fb_flag = False
			app.fb_app_id = fb_app_id
			app.fb_api_key = fb_api_key
			app.fb_secret = fb_secret
			apps = Application.all().filter('isdefault = ',True)
			for i in apps:
				i.isdefault = False
			app.isdefault = True
			app.put()
		return app
	@staticmethod
	def get_by_revision(rev):
		return Application.all().filter('revision = ',rev).get()
	@staticmethod
	def get_app():
		return Application.all().filter('isdefault = ',True).order('-create_at').get()
	@staticmethod
	def get_apps():
		return Application.all().order('-revision')
	
class Tags(db.Model):
	appuser =  db.ReferenceProperty(ApplicationUser,
									collection_name='created')
	title = db.StringProperty(default="")
	description = db.TextProperty(default="")
	create_at = db.DateTimeProperty(auto_now_add=True)
	updated_at = db.DateTimeProperty(auto_now=True)
	level = db.IntegerProperty(default=3)
	count = db.IntegerProperty(default=0)
	
	def set_count(self):
		self.count = int(self.get_count())+1
		self.save()

	def get_count(self):
		return Entry.all().filter('is_draft = ',False).filter('tags = ',self.key()).count()	
	
	@staticmethod
	def find_by_name(name):
		return Tags.all().filter('title = ',name).get()

	@staticmethod
	def tag_pool(span=20):
		try:
			return Tags.all().order('-updated_at').fetch(span)
		except:
			return None
	@property
	def entries(self):
		return Entry.all().filter('tags',self.key())

	# @staticmethod
	# def add_by_name(name):
	# 	tag = Tags.find_by_name(name):
	# 	if not tag:
	# 		tag = Tags()
	# 		tag.appuser = 
			
class Entry(db.Model):
	appuser =  db.ReferenceProperty(ApplicationUser,
									collection_name='create_by')
	title = db.StringProperty(default="")
	content = db.StringProperty(multiline=True)
	full_content = db.TextProperty(default="")
	create_at = db.DateTimeProperty(auto_now_add=True)
	updated_at = db.DateTimeProperty(auto_now=True)
	is_draft = db.BooleanProperty(default=True)
	tags = db.ListProperty(db.Key)
	relation = db.ListProperty(db.Key)
	types = db.StringProperty(choices=set(["entry","diary","memo","file"]))
	# def put(self):
	# 	db.Model.put(self)
		# self.appuser.status_updated_date = datetime.datetime.now()
		# self.appuser.put()
	def relations(self):
		# print self.relation[0]
		return db.get(self.relation[0])
	def set_rss(self):
		result = self.full_content.replace(u"<","&lt;").replace(u">","&gt;").replace(u"&nbsp;","&#160;")
		memcache.set("entry_"+str(self.key()), result)
		return result
	def rss_content(self):
		result = memcache.get("entry_"+str(self.key()))
		if not result:
			result = self.set_rss()
		return result
	def show_date(self):
		date = self.create_at
		date = date + datetime.timedelta(hours=9)
		return date.strftime("%Y/%m/%d %H:%M")
	def show_day(self):
		date = self.create_at
		date = date + datetime.timedelta(hours=9)
		return date.strftime("%Y/%m/%d")
	def show_pub_date(self):
		date = self.create_at
		date = date + datetime.timedelta(hours=9)
		return date.strftime("%a, %d %b %Y %H:%M:%S +0900")
	
	def add_tags(self,tags):
		if tags:
			for name in tags:
				tag = Tags.find_by_name(name)
				if not tag:
					tag = Tags()
					tag.appuser = self.appuser
					tag.title = name
					tag.put()
				tag.set_count()
				tag.save()
				self.tags.append(tag.key())
				self.save()

	def remove_tags(self):
		# tmp = None
		# try:
		# 	if tag in self.tags:
		# 		tmp = db.get(tag)
		# 		tmp -=1
		# 		tmp.save()
		# except:
		# 	pass
		self.tags = []
		self.save()
	def all_tag(self):
		tags = self.tags
		result = []
		tmp = None
		for tag in tags:
			tmp = db.get(tag)
			if tmp and tmp.title:
				result.append(tmp)
		return result
		# return Tags.all().filter('tags = ',self.key()).fetch(1000)
		# result = []
		# tmp = None
		# for tag in tags:
		# 	tmp = db.get(tag)
		# 	# if tmp:
		# 	result.append(tmp)
		# return tags
		# return Tags.all().filter('tags = ',self.key()).fetch(1000)
	@staticmethod
	def set_rss_temp():
		template_values = None
		span = 10
		page = 0
		entries,entry_count = Entry.get_entries(span,page,is_draft=False)
		if entries:
			template_values = {
				'show_latest':Entry.get_recent(1)[0].show_pub_date(),
				'application':Application.get_app(),
				'items':entries,
				}
			memcache.set("rss_entry", template_values)
		return template_values
	@staticmethod
	def get_recent(span=3,get_all=False,is_draft=False,types="",igtype="file"):
		query = Entry.all().order('types')
		if not get_all:
			query.filter('is_draft = ',is_draft)
			if igtype:
				query.filter('types != ',igtype)
			if types:
				query.filter('types = ',types)
		return query.order('-create_at').fetch(span)
	@staticmethod
	def get_entries(span=5,page=0,get_all=False,is_draft=False,types="",igtype="file"):
		query = Entry.all().order('types')
		if not get_all:
			query.filter('is_draft = ',is_draft)
			if igtype:
				query.filter('types != ',igtype)
			if types:
				query.filter('types = ',types)
		query = query.order('-create_at')
		if page!=0:
			page = page*span - span
		return query.fetch(span,page),query.count()
		# return Entry.all().order('-create_at').fetch(span)
