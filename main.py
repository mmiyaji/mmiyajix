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

from model import *
from utility import *
from app_settings import *
from url_handler import *
import admin
logging.basicConfig(level=logging.DEBUG)
class MainPage(NormalRequestHandler):
	def _get(self):
		template_values = None
		if self.application:
			template_values = {
					'now':self.now,
					'user':self.user,
					'appuser':self.appuser,
					'application':self.application,
					'recents':Entry.get_recent(10,is_draft=False),
					'url': self.url,
					'all_tags':Tags.tag_pool(),
					'all_contents':Entry.get_recent(span=100),
				}
			path = os.path.join(os.path.dirname(__file__), './templates/base/index.html')
			self.response.out.write(template.render(path, template_values))	
		else:
			self.redirect('/initialize')

class ErrorPage(webapp.RequestHandler):
	def get(self,status=None):
		code = 401
		if status:
			code = int(status)
		self.error(code)
		self.response.out.write(self.response.http_status_message(code))

class InitPage(NormalRequestHandler):
	def _get(self):
		template_values = None
		template_values = {
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
		isadmin = False
		if users.is_current_user_admin():
			logging.debug("admin")
			isadmin = True
		template_values = {
				'now':self.now,
				'isadmin':isadmin,
				'user':self.user,
				'users':ApplicationUser.get_users(),
				'appuser':self.appuser,
				'application':self.application,
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
			appuser.put()
		if self.application:
			self.redirect("/")
		else:
			self.redirect("/initialize_app")

class EntryPage(NormalRequestHandler):
	def _get(self):
		template_values = None
		entry = None
		view = False
		if self.application:
			if self.request.get("entry_id"):
				entry = Entry.get_by_id(int(self.request.get("entry_id")))
			if self.request.get("view"):
				view = True
			if entry:
				template_values = {
					'title':entry.title,
					'view':view,
					'now':self.now,
					'user':self.user,
					'appuser':self.appuser,
					'application':self.application,
					'entry':entry,
					'url': self.url,
					'all_tags':Tags.tag_pool(),
					'all_contents':Entry.get_recent(span=100),
				}
				path = os.path.join(os.path.dirname(__file__), './templates/base/entry.html')
				self.response.out.write(template.render(path, template_values))
			else:
				template_values = {
					'now':self.now,
					'user':self.user,
					'appuser':self.appuser,
					'application':self.application,
					'url': self.url,
					}
				error_status(self,404,template_values)
		else:
			self.redirect('/initialize')

class PortfolioPage(NormalRequestHandler):
	def _get(self,name):
		template_values = None
		if self.application:
			owner = None
			if name:
				owner = ApplicationUser.get_by_nickname(name)
			if owner:
				template_values = {
					'title':owner.fullname+"'s portfolio",
					'now':self.now,
					'owner':owner,
					'user':self.user,
					'appuser':self.appuser,
					'application':self.application,
					'url': self.url,
				}
				path = os.path.join(os.path.dirname(__file__), './templates/base/portfolio.html')
				self.response.out.write(template.render(path, template_values))
			else:
				template_values = {
					'now':self.now,
					'user':self.user,
					'appuser':self.appuser,
					'application':self.application,
					'url': self.url,
					}
				error_status(self,404,template_values)
		else:
			self.redirect('/initialize')

class EntriesPage(NormalRequestHandler):
	def _get(self):
		template_values = None
		page = 0
		if self.application:
			if self.request.get("page"):
				try:
					page = int(self.request.get("page"))
				except:
					pass
			entries,entry_count = Entry.get_entries(5,page,is_draft=False)
			if entries:
				page_list,pages = get_page_list(page, entry_count, 10)
				template_values = {
					'title':'Entries',
					'now':self.now,
					'user':self.user,
					'appuser':self.appuser,
					'application':self.application,
					'entries':entries,
					'url': self.url,
					'all_tags':Tags.tag_pool(),
					'all_contents':Entry.get_recent(span=100,is_draft=False),
					}
				path = os.path.join(os.path.dirname(__file__), './templates/base/entries.html')
				self.response.out.write(template.render(path, template_values))
			else:
				template_values = {
					'now':self.now,
					'user':self.user,
					'appuser':self.appuser,
					'application':self.application,
					'url': self.url,
					}
				error_status(self,404,template_values)
		else:
			self.redirect('/initialize')
	
application = webapp.WSGIApplication(
	[
	('/', MainPage),
	('/error/(.*)', ErrorPage),
	('/manage', admin.ManagePage),
	('/edit', admin.EditPage),
	('/editor', admin.EditorPage),
	('/ajax_post/(.*)', admin.AjaxPostPage),
	('/portfolio/(.*)', PortfolioPage),
	('/entry', EntryPage),
	('/entries', EntriesPage),
	('/registration', RegistrationPage),
	('/initialize', InitPage),
	('/initialize_app', admin.CreateAppPage),
	],debug=True)

def main():
	run_wsgi_app(application)

if __name__ == "__main__":
	main()