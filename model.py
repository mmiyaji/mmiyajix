# -*- coding: utf-8 -*-
from google.appengine.ext import db
from utility import *
import datetime
from time import gmtime, strftime
from app_settings import *

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
	
	@staticmethod
	def create_app(title="",rev=0,description="",appuser=None,img_url=""):
		app = None
		if Application.all().filter("rev = ",rev).count() < 1:
			app = Application()
			app.title = title
			app.description = description
			app.create_appuser = appuser
			app.img_url = img_url
			app.revision = rev
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

class Entry(db.Model):
	appuser =  db.ReferenceProperty(ApplicationUser,
									collection_name='create_by')
	title = db.StringProperty(default="")
	content = db.StringProperty(multiline=True)
	full_content = db.TextProperty(default="")
	create_at = db.DateTimeProperty(auto_now_add=True)
	updated_at = db.DateTimeProperty(auto_now=True)
	tags = db.ListProperty(db.Key)
	def put(self):
		db.Model.put(self)
		# self.appuser.status_updated_date = datetime.datetime.now()
		# self.appuser.put()
		
	def show_date(self):
		date = self.date
		date = date + datetime.timedelta(hours=9)
		return date.strftime("%Y-%m-%d %H:%M")
	
	@staticmethod
	def get_recent(span=3):
		return Entry.all().order('-create_at').fetch(span)
	