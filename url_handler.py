# encoding: utf-8
"""
url_handler.py

Created by Masahiro MIYAJI on 2011-02-23.
Copyright (c) 2011 ISDL. All rights reserved.
"""
from utility import *
from model import *
from app_settings import *

logging.basicConfig(level=logging.DEBUG)
class AbstractRequestHandler(webapp.RequestHandler):
	def __init__(self):
		logging.getLogger().setLevel(logging.DEBUG)
		self.user = None
		self.appuser = None
		self.application = None
		self.url = None
		self.now = get_now()
	def auth(self):
		self.user = users.get_current_user()
		if not self.user:
			url = users.create_login_url(self.request.uri)
			self.redirect(url)
			return False
		else:
			self.appuser = ApplicationUser.get_by_user(self.user)
			if not ApplicationUser.auth(self.user):
				self.redirect('/registration')
				return False
			else:
				return True
	
	def google_auth(self):
		if not self.user:
			self.user = users.get_current_user()
		if self.user:
			return True
		else:
			return False
	
	def app_auth(self):
		if self.google_auth():
			if not self.appuser:
				self.appuser = ApplicationUser.get_by_user(self.user)
			if not self.appuser:
				return False
			else:
				return True
		else:
			return False
			
	def admin_auth(self):
		if self.app_auth() and self.appuser.role == "admin":
			return True
		else:
			return False

# Basic認証 ユーザ作成時などに読み込む
class BasicAuthentication(AbstractRequestHandler):
	def __init__(self):
		logging.getLogger().setLevel(logging.DEBUG)
		self.url = None
		self.user = None
		self.appuser = None
		self.application = Application.get_app()
		self.now = get_now()
		
	def get(self):
		self.user = users.get_current_user()
		if not self.user:
			self.redirect(users.create_login_url(self.request.uri))
		else:
			self.appuser = ApplicationUser.get_by_user(self.user)
			if self.appuser:
				self.url = users.create_logout_url(self.request.uri)
				self._get()
			else:
				self.url = users.create_logout_url(self.request.uri)
				if users.is_current_user_admin():
					self._get()
				else:
					if self.basic_auth():
						self._get()
					else:
						code=401
						self.error(code)
						self.response.out.write(self.response.http_status_message(code))
	def post(self):
		self.user = users.get_current_user()
		if not self.user:
			self.redirect(users.create_login_url(self.request.uri))
		else:
			self.appuser = ApplicationUser.get_by_user(self.user)
			if self.appuser:
				self.url = users.create_logout_url(self.request.uri)
				self._post()
			else:
				self.url = users.create_logout_url(self.request.uri)
				if users.is_current_user_admin():
					self._post()
				else:
					if self.basic_auth():
						self.appuser = ApplicationUser.get_by_user(self.user)
						self.url = users.create_logout_url(self.request.uri)
						self._post()
					else:
						code = 401
						self.error(code)
						self.response.out.write(self.response.http_status_message(code))

	def basic_auth(self):
		auth_header = self.request.headers.get('Authorization')
		isbase = False
		if self.application:
			if self.application.islock:
				isbase = True
				base_user = self.application.super_user
				base_pass = self.application.super_pass
		if isbase:
			if auth_header:
				try:
					(scheme, base64) = auth_header.split(' ')
					if scheme != 'Basic':
						return False
					(username, password) = b64decode(base64).split(':')
					if username == base_user and create_hash(password) == base_pass:
						return True
				except (ValueError, TypeError), err:
					logging.warn(type(err))
					return False
			self.response.set_status(401)
			self.response.headers['WWW-Authenticate'] = 'Basic realm="'+self.application.title+'"'
		else:
			return True

# 
class ModifyRequestHandler(AbstractRequestHandler):
	def get(self):
		self.user = users.get_current_user()
		self.appuser = ApplicationUser.get_by_user(self.user)
		self.url = users.create_login_url(self.request.uri)
		self.application = Application.get_app()
		if self.appuser and self.appuser.modify_auth():
			self._get()
		else:
			template_values = {
				'now':self.now,
				'user':self.user,
				'appuser':self.appuser,
				'application':self.application,
				'url': self.url,
				}
			error_status(self,401,template_values)
	
	def post(self):
		self.user = users.get_current_user()
		self.appuser = ApplicationUser.get_by_user(self.user)
		self.url = users.create_login_url(self.request.uri)
		self.application = Application.get_app()
		if self.appuser and self.appuser.modify_auth():
			self._post()
		else:
			template_values = {
				'now':self.now,
				'user':self.user,
				'appuser':self.appuser,
				'application':self.application,
				'url': self.url,
				}
			error_status(self,401,template_values)

# 
class AjaxRequestHandler(AbstractRequestHandler):
	def get(self,status):
		self.user = users.get_current_user()
		self.appuser = ApplicationUser.get_by_user(self.user)
		if self.appuser and self.appuser.modify_auth():
			self.url = users.create_login_url(self.request.uri)
			self.application = Application.get_app()
			self._get(status)
		else:
			code = 401
			self.error(code)
			self.response.out.write(self.response.http_status_message(code))
	
	def post(self,status):
		self.user = users.get_current_user()
		self.appuser = ApplicationUser.get_by_user(self.user)
		if self.appuser and self.appuser.modify_auth():
			self.url = users.create_login_url(self.request.uri)
			self.application = Application.get_app()
			self._post(status)
		else:
			code = 401
			self.error(code)
			self.response.out.write(self.response.http_status_message(code))

# 
class NormalRequestHandler(AbstractRequestHandler):
	def get(self,status=None):
		self.url = users.create_login_url(self.request.uri)
		self.user = users.get_current_user()
		self.appuser = ApplicationUser.get_by_user(self.user)
		self.application = Application.get_app()
		if status:
			self._get(status)
		else:
			self._get()

	def post(self,status=None):
		self.url = users.create_login_url(self.request.uri)
		self.user = users.get_current_user()
		self.appuser = ApplicationUser.get_by_user(self.user)
		self.application = Application.get_app()
		if status:
			self._post(status)
		else:
			self._post()

# 
class StatusRequestHandler(AbstractRequestHandler):
	def get(self,status):
		self.url = users.create_login_url(self.request.uri)
		self.user = users.get_current_user()
		self.appuser = ApplicationUser.get_by_user(self.user)
		self.application = Application.get_app()
		self._get(status)
	def post(self,status):
		self.url = users.create_login_url(self.request.uri)
		self.user = users.get_current_user()
		self.appuser = ApplicationUser.get_by_user(self.user)
		self.application = Application.get_app()
		self._post(status)
