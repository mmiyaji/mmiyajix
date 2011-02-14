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

import os,urllib,random,datetime
from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext.webapp import util
from google.appengine.ext.webapp.util import run_wsgi_app
import wsgiref.handlers
from google.appengine.api import mail

from google.appengine.ext.webapp import template
from model import *
from utility import *
from app_settings import *

class AbstractRequestHandler(webapp.RequestHandler):
	def __init__(self):
		self.user = None
		self.appuser = None
		
	def auth(self):
		self.user = users.get_current_user()
		if not self.user:
			url = users.create_login_url(self.request.uri)
			self.redirect(url)
			return False
		else:
			self.appuser = ApplicationUser.find_by_user(self.user)
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
				self.appuser = ApplicationUser.find_by_user(self.user)
			if not ApplicationUser.auth(self.user):
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
			
	def get(self):
		if not self.google_auth():
			url = users.create_login_url(self.request.uri)
			self.redirect(url)
		elif not self.app_auth():
			self.redirect('/registration')
		else:
			self._get()
	
	def post(self):
		if not self.google_auth():
			url = users.create_login_url(self.request.uri)
			self.redirect(url)
		elif not self.app_auth():
			self.redirect('/registration')
		else:
			self._post()

class MainPage(webapp.RequestHandler):
	def get(self):
		now = datetime.datetime.now() + datetime.timedelta(hours=9)
		user = users.get_current_user()
		url = None
		template_values = None
		if user:
			url = users.create_logout_url(self.request.uri)
		else:
			url = users.create_login_url(self.request.uri)
		application = Application.get_app()
		if application:
			template_values = {
					'app':application,
					'now':now,
					'user':user,
					'url': url,
				}
			path = os.path.join(os.path.dirname(__file__), './templates/index.html')
		else:
			template_values = {
					'title':'application',
					'now':now,
					'user':user,
					'url': url,
				}
			path = os.path.join(os.path.dirname(__file__), './templates/base/index.html')
		self.response.out.write(template.render(path, template_values))	
		
application = webapp.WSGIApplication(
	[('/', MainPage),
	],debug=True)

def main():
	run_wsgi_app(application)

if __name__ == "__main__":
	main()