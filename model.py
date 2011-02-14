# -*- coding: utf-8 -*-
from google.appengine.ext import db
from utility import *
import datetime
from time import gmtime, strftime
from app_settings import *

class ApplicationUser(db.Model):
	user = db.UserProperty()
	role = db.StringProperty(choices=set(["admin", "user", "developper"]))
	nickname = db.StringProperty(default="")
	email_addr = db.StringProperty(default="")
	fullname = db.StringProperty(default="")
	img_url = db.StringProperty(default="")
	introduction = db.TextProperty(default="")
	create_at = db.DateTimeProperty(auto_now_add=True)
	updated_at = db.DateTimeProperty(auto_now_add=True)

class Revision(db.Model):
	revision = db.IntegerProperty(default=0)
	create_appuser = db.ReferenceProperty(ApplicationUser,
									collection_name='commiter')
	create_at = db.DateTimeProperty(auto_now_add=True)
	updated_at = db.DateTimeProperty(auto_now_add=True)
	
	@staticmethod
	def get_rev(rev=0):
		revision = Revision.all().filter("revision = ",rev).get()
		return revision
	@staticmethod
	def create_revision(rev=0,appuser=None):
		revision = Revision()
		revision.revision = rev
		revision.create_appuser = appuser
		revision.put()
		return revision
	
class Application(db.Model):
	title = db.StringProperty(default="")
	description = db.TextProperty(default="")
	revision = db.ReferenceProperty(Revision,
									collection_name='current_version')
	img_url = db.StringProperty(default="")
	create_appuser = db.ReferenceProperty(ApplicationUser,
									collection_name='created_user')
	create_at = db.DateTimeProperty(auto_now_add=True)
	updated_at = db.DateTimeProperty(auto_now_add=True)
	
	@staticmethod
	def create_app(title="",rev=1,description="",appuser=None,img_url=""):
		app = Application()
		app.title = title
		app.description = description
		app.create_appuser = appuser
		app.img_url = img_url
		
		revision = Revision.get_rev(rev)
		if not revision:
			revision = Revision.create_revision(rev,appuser)
		app.revision = revision
		app.put()
		return app
	
	@staticmethod
	def get_app():
		return Application.all().order('-create_at').get()

class Tags(db.Model):
	appuser =  db.ReferenceProperty(ApplicationUser,
									collection_name='created')
	title = db.StringProperty(default="")
	description = db.TextProperty(default="")
	create_at = db.DateTimeProperty(auto_now_add=True)
	updated_at = db.DateTimeProperty(auto_now_add=True)

class Entry(db.Model):
	appuser =  db.ReferenceProperty(ApplicationUser,
									collection_name='create_by')
	title = db.StringProperty(default="")
	content = db.StringProperty(multiline=True)
	full_content = db.TextProperty(default="")
	create_at = db.DateTimeProperty(auto_now_add=True)
	updated_at = db.DateTimeProperty(auto_now_add=True)
	tags = db.ListProperty(db.Key)
	def put(self):
		db.Model.put(self)
		# self.appuser.status_updated_date = datetime.datetime.now()
		# self.appuser.put()
