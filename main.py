# -*- coding: utf-8 -*-
#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

import os,urllib,random,datetime,logging
from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext.webapp import util
from google.appengine.ext.webapp.util import run_wsgi_app
import wsgiref.handlers
from google.appengine.api import mail
from base64 import b64decode
from google.appengine.ext.webapp import template
from model import *
from utility import *
from app_settings import *

logging.basicConfig(level=logging.DEBUG)
class AbstractRequestHandler(webapp.RequestHandler):
	def __init__(self):
		logging.getLogger().setLevel(logging.DEBUG)
		self.user = None
		self.appuser = None
		self.application = None
		self.url = None
		self.now = datetime.datetime.now() + datetime.timedelta(hours=9)
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
		self.now = datetime.datetime.now() + datetime.timedelta(hours=9)
		
	def get(self):
		self.user = users.get_current_user()
		if not self.user:
			self.redirect(users.create_login_url(self.request.uri))
		else:
			if self.__basicAuth():
				self.appuser = ApplicationUser.get_by_user(self.user)
				self.url = users.create_logout_url(self.request.uri)
				self._get()
			else:
				code = 401
				self.error(code)
				self.response.out.write(self.response.http_status_message(code))
	def post(self):
		self.user = users.get_current_user()
		if not self.user:
			self.redirect(users.create_login_url(self.request.uri))
		else:
			if self.__basicAuth():
				self.appuser = ApplicationUser.get_by_user(self.user)
				self.url = users.create_logout_url(self.request.uri)
				self._post()
			else:
				code = 401
				self.error(code)
				self.response.out.write(self.response.http_status_message(code))

	def __basicAuth(self):
		auth_header = self.request.headers.get('Authorization')
		if auth_header:
			try:
				(scheme, base64) = auth_header.split(' ')
				if scheme != 'Basic':
					return False
				(username, password) = b64decode(base64).split(':')
				if username == BASE_USER and password == BASE_PASS:
					return True
			except (ValueError, TypeError), err:
				logging.warn(type(err))
				return False
		self.response.set_status(401)
		self.response.headers['WWW-Authenticate'] = 'Basic realm="mmiyajix"'

# 
class NormalRequestHandler(AbstractRequestHandler):
	def get(self):
		self.url = users.create_login_url(self.request.uri)
		self.user = users.get_current_user()
		self.appuser = ApplicationUser.get_by_user(self.user)
		self.application = Application.get_app()
		self._get()
	
	def post(self):
		self.url = users.create_login_url(self.request.uri)
		self.user = users.get_current_user()
		self.appuser = ApplicationUser.get_by_user(self.user)
		self.application = Application.get_app()
		self._post()

class MainPage(NormalRequestHandler):
	def _get(self):
		template_values = None
		if self.application:
			template_values = {
					'title':'mmiyajix',
					'now':self.now,
					'user':self.user,
					'appuser':self.appuser,
					'application':self.application,
					'url': self.url,
				}
			path = os.path.join(os.path.dirname(__file__), './templates/base/index.html')
			self.response.out.write(template.render(path, template_values))	
		else:
			self.redirect('/initialize')

class InitPage(NormalRequestHandler):
	def _get(self):
		template_values = None
		template_values = {
				'title':'mmiyajix',
				'now':self.now,
				'user':self.user,
				'appuser':self.appuser,
				'application':self.application,
				'url': self.url,
			}
		path = os.path.join(os.path.dirname(__file__), './templates/base/first.html')
		self.response.out.write(template.render(path, template_values))	
		
class RegistrationPage(BasicAuthentication):
	def _get(self):
		template_values = None
		template_values = {
				'title':'mmiyajix',
				'now':self.now,
				'user':self.user,
				'users':ApplicationUser.get_users(),
				'appuser':self.appuser,
				'url': self.url,
			}
		path = os.path.join(os.path.dirname(__file__), './templates/base/registration.html')
		self.response.out.write(template.render(path, template_values))
	def _post(self):
		if self.request.get("nickname"):
			if self.appuser:
				appuser = self.appuser
			else:
				appuser = ApplicationUser()
			appuser.user = self.user
			appuser.nickname = self.request.get("nickname")
			appuser.role = self.request.get("group")
			appuser.img_url = self.request.get("img_url")
			appuser.description = self.request.get("description")
			appuser.fullname = self.request.get("fullname")
			appuser.email_addr = self.request.get("email_addr")
			if self.appuser:
				appuser.save()
			else:
				appuser.put()
		self.redirect("/")
	
class CreateAppPage(BasicAuthentication):
	def _get(self):
		if self.appuser:
			template_values = None
			template_values = {
				'title':'mmiyajix',
				'now':self.now,
				'user':self.user,
				'appuser':self.appuser,
				'application':self.application,
				'applications':Application.get_apps(),
				'url': self.url,
				}
			path = os.path.join(os.path.dirname(__file__), './templates/base/initapp.html')
			self.response.out.write(template.render(path, template_values))
		else:
			self.redirect("/registration")

	def _post(self):
		if self.request.get("title"):
			if self.request.get("application"):
				application = Application.get_by_id(int(self.request.get("application")))
			else:
				application = Application()
			application.create_appuser = self.appuser
			application.title = self.request.get("title")
			application.revision = int(self.request.get("revision"))
			application.img_url = self.request.get("img_url")
			application.description = self.request.get("description")
			if self.request.get("application"):
				application.save()
			else:
				application.put()
		self.redirect("/")
application = webapp.WSGIApplication(
	[
	('/', MainPage),
	('/registration', RegistrationPage),
	('/initialize', InitPage),
	('/initialize_app', CreateAppPage),
	],debug=True)

def main():
	run_wsgi_app(application)

if __name__ == "__main__":
	main()