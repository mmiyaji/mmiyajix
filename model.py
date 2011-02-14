# -*- coding: utf-8 -*-
from google.appengine.ext import db
from utility import *
import datetime
from time import gmtime, strftime
from user_settings import *
from cgi import escape
import re
import random

class ApplicationUser(db.Model):
	user = db.UserProperty()
	role = db.StringProperty(choices=set(["admin", "user", "bot"]))
	nickname = db.StringProperty()
	img_url = db.StringProperty(default="")
	
	def registration(self,registration_request,user,role="user"):
		if registration_request.get("user") == REGISTRATION_USER and registration_request.get("password") == REGISTRATION_PASSWORD:
			if not ApplicationUser.auth(user):
				self.user = user
				self.role = role
				self.nickname = user.nickname()
				while ApplicationUser.all().filter('nickname = ',self.nickname).count() != 0:
					self.nickname = self.nickname + str(random.randint(0,1000))
				
				self.put()
			return True
		else:
			return False

	@staticmethod
	def auth(user,role=""):
		app_users = ApplicationUser.all()
		if role!="":
			app_user = app_users.filter('user = ', user).filter('role = ', role)
		else:
			app_user = app_users.filter('user = ', user)
			
		if app_user.count() > 0:
			return True
		else:
			return False
	
	@staticmethod
	def find_by_user(user):
		if ApplicationUser.all().filter("user = ",user).count() == 1:
			return ApplicationUser.all().filter("user = ",user).fetch(1)[0]
		else:
			return None
	@staticmethod
	def find_by_nickname(nickname):
		if ApplicationUser.all().filter("nickname = ",nickname).count() == 1:
			return ApplicationUser.all().filter("nickname = ",nickname).fetch(1)[0]
		else:
			return None

class Projects(db.Model):
	author = db.ReferenceProperty(ApplicationUser,
									collection_name='author')
	latest_update_user = db.ReferenceProperty(ApplicationUser,
									collection_name='updater')
	title = db.StringProperty()
	comment = db.StringProperty(multiline=True)
	
	create_at = db.DateTimeProperty(auto_now_add=True)
	update_at = db.DateTimeProperty()
	
	def tag(self):
		return (x.tag for x in self.ProjectTag_set)
	
	def show_create(self):
		date = self.create_at
		now = datetime.datetime.now()
		# if now - date < datetime.timedelta(hours=24):
		# 	if (now - date).seconds/3600 > 0:
		# 		return "約" + str(int((now - date).seconds/3600) + (1 if (now - date).seconds%3600 > 1800 else 0 )) + "時間前"
		# 	elif (now - date).seconds/60 > 0:
		# 		return "約" + str(int((now - date).seconds/60) + 1) + "分前"
		# 	else:
		# 		return "約" + str(int((now - date).seconds) + 1) + "秒前"
		# else:
			#6:45 PM Sep 18th
		date = date + datetime.timedelta(hours=9)
		# return date
		# return date.strftime("%a, %d %b %Y %H:%M:%S")
		return date.strftime("%Y-%m-%d %H:%M:%S")
			
	def show_update(self):
		date = self.update_at
		now = datetime.datetime.now()
		# if now - date < datetime.timedelta(hours=24):
		# 	if (now - date).seconds/3600 > 0:
		# 		return "約" + str(int((now - date).seconds/3600) + (1 if (now - date).seconds%3600 > 1800 else 0 )) + "時間前"
		# 	elif (now - date).seconds/60 > 0:
		# 		return "約" + str(int((now - date).seconds/60) + 1) + "分前"
		# 	else:
		# 		return "約" + str(int((now - date).seconds) + 1) + "秒前"
		# else:
			#6:45 PM Sep 18th
		date = date + datetime.timedelta(hours=9)
		# return date
		return date.strftime("%Y-%m-%d %H:%M:%S")
	
	def show_tags(self):
		protag = ProjectTag.all().filter('project = ',self).fetch(FETCH_SPAN)
		tags = []
		for pt in protag:
			tags.append(pt.tag)

		return tags
	
	
	@staticmethod
	def get_list(postuser=None,search_status=None, search_span=FETCH_SPAN):
		query = Projects.all().order('-create_at')
		if postuser!=None:
			query = query.filter('appuser = ',postuser)

		if search_status==None:
			statuses = query.fetch(int(search_span))
			#statuses = query.fetch(15)
		else:
			query = query.filter('create_at >= ', search_status.date)
			statuses = query.fetch(1000)
		
		return statuses
	
class Codes(db.Model):
	author = db.ReferenceProperty(ApplicationUser)
	title = db.StringProperty()
	# number = db.StringProperty()
	# content = db.ReferenceProperty(ApplicationUser)
	content = db.TextProperty()
	comment = db.StringProperty(multiline=True)
	create_at = db.DateTimeProperty(auto_now_add=True)
	update_at = db.DateTimeProperty()
	
	@staticmethod
	def validate_code(txt):
		if Codes.all().filter("content = ",txt).count() == 1:
			return Codes.all().filter("content = ",txt).fetch(1)[0]
		else:
			return None
	
	@staticmethod
	def get_list(postuser=None,search_status=None, search_span=FETCH_SPAN):
		query = Codes.all()
		statuses = query.fetch(FETCH_SPAN)
		
		return statuses

class Memories(db.Model):
	author = db.ReferenceProperty(ApplicationUser)
	title = db.StringProperty()
	content = db.TextProperty()
	comment = db.StringProperty(multiline=True)
	create_at = db.DateTimeProperty(auto_now_add=True)
	update_at = db.DateTimeProperty()
	
	@staticmethod
	def validate_memory(txt):
		if Memories.all().filter("content = ",txt).count() == 1:
			return Memories.all().filter("content = ",txt).fetch(1)[0]
		else:
			return None
	
	@staticmethod
	def get_list(postuser=None,search_status=None, search_span=FETCH_SPAN):
		query = Memories.all()
		statuses = query.fetch(FETCH_SPAN)
		
		return statuses
	
		
class Tags(db.Model):
	content = db.StringProperty()
	is_language = db.BooleanProperty(default=False)
	create_at = db.DateTimeProperty(auto_now_add=True)

	def codes(self):
		return (x.project for x in self.ProjectTag_set)
	
	def create(self):
		db.Model.put(self)
		self.appuser.put()

	def get_grouptag_name(self):
		protag = ProjectTag.get_project(self)
		tags = []
		
		for pro in protag:
			ptag = ProjectTag.get_tag(pro.project)
			for p in ptag:
				if tags.count(p.tag)==0:
					tags.append(p.tag)
		tags.sort()
		# tags.reverse()
		return tags
		# all().filter("tag = ",tag).fetch(FETCH_SPAN)

	@staticmethod
	def validate_tag(txt):
		if Tags.all().filter("content = ",txt).count() == 1:
			return Tags.all().filter("content = ",txt).fetch(1)[0]
		else:
			return None

	@staticmethod
	def get_list(postuser=None,search_status=None, search_span=FETCH_SPAN):
		statuses = Tags.all().order('content').fetch(FETCH_SPAN)
		return statuses

	@staticmethod
	def find_by_name(content):
		if Tags.all().filter("content = ",content).count() == 1:
			return Tags.all().filter("content = ",content).fetch(1)[0]
		else:
			return None

	
class ProjectCode(db.Model):
	code = db.ReferenceProperty(Codes)
	project = db.ReferenceProperty(Projects)
	create_at = db.DateTimeProperty(auto_now_add=True)
	
	@staticmethod
	def get_code(pro):
		query = ProjectCode.all()
		query = query.filter('project = ',pro)
		codes = query.fetch(1000)
		return codes
	
	@staticmethod
	def get_project(code):
		return ProjectCode.all().filter('code = ',code).fetch(1000)
	
	
class ProjectTag(db.Model):
	tag = db.ReferenceProperty(Tags)
	project = db.ReferenceProperty(Projects)
	create_at = db.DateTimeProperty(auto_now_add=True)
	
	@staticmethod
	def get_tag(pro):
		query = ProjectTag.all()
		query = query.filter('project = ',pro)
		tags = query.fetch(1000)
		return tags
		
	@staticmethod
	def get_project(tag):
		query = ProjectTag.all()
		query = query.filter('tag = ',tag)
		projects = query.fetch(1000)
		return projects
	

class CodeMemory(db.Model):
	code = db.ReferenceProperty(Codes)
	memory = db.ReferenceProperty(Memories)
	create_at = db.DateTimeProperty(auto_now_add=True)
	
	@staticmethod
	def get_memory(code):
		query = CodeMemory.all()
		query = query.filter('code = ',code)
		memories = query.fetch(1000)
		return memories
	
	@staticmethod
	def get_latest_memory(code):
		if CodeMemory.all().filter("code = ",code).count() == 1:
			return CodeMemory.all().order('-create_at').filter("code = ",code).fetch(1)[0]
		else:
			return None
	
	@staticmethod
	def get_code(mem):
		query = CodeMemory.all()
		query = query.filter('memory = ',mem)
		codes = query.fetch(1000)
		return codes

class Histories(db.Model):
	author = db.ReferenceProperty(ApplicationUser)
	project = db.ReferenceProperty(Projects)
	action = db.StringProperty()
	create_at = db.DateTimeProperty(auto_now_add=True)

	def show_create(self):
		date = self.create_at
		now = datetime.datetime.now()
		date = date + datetime.timedelta(hours=9)
		return date.strftime("%Y-%m-%d %H:%M")

	
	@staticmethod
	def get_list(postuser=None,search_status=None, search_span=FETCH_SPAN):
		statuses = Histories.all().order('-create_at').fetch(FETCH_SPAN)
		return statuses

class Status(db.Model):
	appuser =  db.ReferenceProperty(ApplicationUser,
									collection_name='statuses')
	content = db.StringProperty(multiline=True)
	date = db.DateTimeProperty(auto_now_add=True)
	reply_target = db.IntegerProperty()
	rt_target = db.IntegerProperty()
	target_user = db.ReferenceProperty(ApplicationUser,
									collection_name='replys')
	target_group_id = db.IntegerProperty()
	room_id = db.IntegerProperty()
	create_room_id = db.IntegerProperty()
	come_in_room_id = db.IntegerProperty()
	
	favorite_users = db.ListProperty(db.Key)

	def put(self):
		db.Model.put(self)
		self.appuser.status_updated_date = datetime.datetime.now()
		self.appuser.put()
