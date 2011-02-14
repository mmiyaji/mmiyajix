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

import cgi

from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.runtime.apiproxy_errors import CapabilityDisabledError

import os
from google.appengine.ext.webapp import template
import datetime 
from model import *
from utility import *

import wsgiref.handlers
import gdata.service
import gdata.photos.service
import gdata.alt.appengine
import urllib
from google.appengine.api import mail

from user_settings import *
import random
import string
from google.appengine.ext import webapp
from google.appengine.ext.webapp import util

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

class Isdl_Edit(webapp.RequestHandler):
	def get(self):
		template_values = {}
		path = os.path.join(os.path.dirname(__file__), './templates/isdl_edit.html')
		self.response.out.write(template.render(path, template_values))

class Inner_Edit(webapp.RequestHandler):
	def get(self):
		template_values = {}
		path = os.path.join(os.path.dirname(__file__), './templates/innereditor.html')
		self.response.out.write(template.render(path, template_values))

class Clustering(webapp.RequestHandler):
	def get(self):
		template_values = {}
		path = os.path.join(os.path.dirname(__file__), './bin-debug/Clusteringer.html')
		self.response.out.write(template.render(path, template_values))
class Kmeans(webapp.RequestHandler):
	def get(self):
		template_values = {}
		path = os.path.join(os.path.dirname(__file__), './templates/kmeans.html')
		self.response.out.write(template.render(path, template_values))

class Fuzzy(webapp.RequestHandler):
	def get(self):
		template_values = {}
		path = os.path.join(os.path.dirname(__file__), './templates/fuzzy.html')
		self.response.out.write(template.render(path, template_values))

class Preview(webapp.RequestHandler):
	def get(self):
		template_values = {}
		path = os.path.join(os.path.dirname(__file__), './templates/preview.html')
		self.response.out.write(template.render(path, template_values))
		
		
class MainPage(webapp.RequestHandler):
	def get(self):
		# 
		# projects = Projects.get_list()
		# histories = Histories.get_list()
		# # all_tags = []
		# # for project in projects:
		# # 	protag = ProjectTag.all().filter('project = ',project).fetch(FETCH_SPAN)
		# # 	tags = []
		# # 	for pt in protag:
		# # 		tags.append(pt.tag)
		# # 	all_tags.append(tags)
		# 
		# all_tags = Tags.get_list()
		# 
		template_values = {
									# 'projects': projects,
									# 'histories': histories,
									# 'all_tags': all_tags,
									# # 'all_tags': all_tags,
									# 'appuser':self.appuser,
									# 'current_user':self.user,
									'title':"m-codes",
									'logout_url': users.create_logout_url(self.request.uri),
									}	
		path = os.path.join(os.path.dirname(__file__), './templates/main.html')
		self.response.out.write(template.render(path, template_values))

class MakeProject(AbstractRequestHandler):
	def _get(self):
		all_tags = Tags.get_list()
		template_values = {
									'all_tags': all_tags,
									'appuser':self.appuser,
									'current_user':self.user,
									'logout_url': users.create_logout_url(self.request.uri),
									}	
		path = os.path.join(os.path.dirname(__file__), './templates/project_form.html')
		self.response.out.write(template.render(path, template_values))

class ProjectPage(AbstractRequestHandler):
	def _get(self):
		project = Projects.get_by_id(int(self.request.get('pid')))
		protag = ProjectTag.all().filter('project = ',project).fetch(FETCH_SPAN)
		# procode = ProjectCode.all().filter('project = ',project).order('-create_at').fetch(FETCH_SPAN)
		procode = ProjectCode.all().filter('project = ',project).fetch(FETCH_SPAN)
		
		codmem = CodeMemory.all().fetch(FETCH_SPAN)
		all_tags = Tags.get_list()
		
		tags = []
		for pt in protag:
			tags.append(pt.tag)
		tags.sort()
				
		codes = []
		for pc in procode:
			codes.append(CodeMemory.get_latest_memory(pc.code))
		
		cod = Codes()
		cod.content = "Null"
		codes.append(cod)
		
		# codes = ProjectCode.get_code(project)
		template_values = {
									'project': project,
									'all_tags': all_tags,
									'tags': tags,
									'codes': codes,
									'codmem': codmem,
									'appuser':self.appuser,
									'current_user':self.user,
									'logout_url': users.create_logout_url(self.request.uri),
									}	
		path = os.path.join(os.path.dirname(__file__), './templates/project.html')
		self.response.out.write(template.render(path, template_values))

class TagPage(AbstractRequestHandler):
	def _get(self):
		tag = Tags.get_by_id(int(self.request.get('tid')))
		protag = ProjectTag.all().filter('tag = ',tag).fetch(FETCH_SPAN)
		# procode = ProjectCode.all().filter('project = ',project).order('-create_at').fetch(FETCH_SPAN)
		# procode = ProjectCode.all().filter('project = ',project).fetch(FETCH_SPAN)
		all_tags = Tags.get_list()
		
		projects = []
		for pt in protag:
			projects.append(pt.project)
				
		# codes = ProjectCode.get_code(project)
		template_values = {
									'projects': projects,
									'all_tags': all_tags,
									'tag': tag,
									# 'codes': codes,
									'appuser':self.appuser,
									'current_user':self.user,
									'logout_url': users.create_logout_url(self.request.uri),
									}	
		path = os.path.join(os.path.dirname(__file__), './templates/tag.html')
		self.response.out.write(template.render(path, template_values))

class SearchPage(AbstractRequestHandler):
	def _get(self):
		# tag = Tags.get_by_id(int(self.request.get('tid')))
		# protag = ProjectTag.all().filter('tag = ',tag).order('-create_at').fetch(FETCH_SPAN)
		# procode = ProjectCode.all().filter('project = ',project).order('-create_at').fetch(FETCH_SPAN)
		# procode = ProjectCode.all().filter('project = ',project).fetch(FETCH_SPAN)
				
		# projects = []
		# for pt in protag:
		# 	projects.append(pt.project)
				
		# codes = ProjectCode.get_code(project)
		template_values = {
									# 'projects': projects,
									# 'tag': tag,
									# 'codes': codes,
									'all_tags': all_tags,
									'appuser':self.appuser,
									'current_user':self.user,
									'logout_url': users.create_logout_url(self.request.uri),
									}	
		path = os.path.join(os.path.dirname(__file__), './templates/search.html')
		self.response.out.write(template.render(path, template_values))



class AddCode(AbstractRequestHandler):
	def _get(self):
		project = Projects.get_by_id(int(self.request.get('pid')))
		# protag = ProjectTag.all().filter('project = ',project).fetch(FETCH_SPAN)
		protag = ProjectTag.get_tag(project)
		all_tags = Tags.get_list()
		
		tags = []
		for pt in protag:
			tags.append(pt.tag)
		tags.sort()
		
		template_values = {
									'project': project,
									'all_tags': all_tags,
									'tags': tags,
									'appuser':self.appuser,
									'current_user':self.user,
									'logout_url': users.create_logout_url(self.request.uri),
									}	
		path = os.path.join(os.path.dirname(__file__), './templates/code_form.html')
		self.response.out.write(template.render(path, template_values))


class EditCode(AbstractRequestHandler):
	def _get(self):
		code = Codes.get_by_id(int(self.request.get('cid')))
		project = Projects.get_by_id(int(self.request.get('pid')))
		procode = ProjectCode.get_project(code)
		# codmem = CodeMomory.get_memory(code)
		protag = ProjectTag.get_tag(project)
		all_tags = Tags.get_list()
		
		tags = []
		for pt in protag:
			tags.append(pt.tag)
		tags.sort()
		
		# codes = []
		# for pc in procode:
		# 	codes.append()
		codes = CodeMemory.get_latest_memory(code)
		
		template_values = {
									'project': project,
									'codes': codes,
									'all_tags': all_tags,
									'tags': tags,
									'appuser':self.appuser,
									'current_user':self.user,
									'logout_url': users.create_logout_url(self.request.uri),
									}	
		path = os.path.join(os.path.dirname(__file__), './templates/code_edit.html')
		self.response.out.write(template.render(path, template_values))


class ProjectPost(AbstractRequestHandler):
	def _post(self):
		project = Projects()
		project.author = self.appuser
		project.title = self.request.get('title')
		project.comment = self.request.get('comment')
		project.update_at = datetime.datetime.now()
		project.latest_update_user = self.appuser
		
		txt = self.request.get('tags')
		tags = txt.split(",")

		txt1 = self.request.get('langs')
		langs = txt1.split(",")

		history = Histories()
		
		try:
			project.put()
			history.author = project.author
			history.project = project
			history.action = "add_project"
			history.put()
			if langs!="":
				for lang in langs:
					t = Tags.validate_tag(lang)
					if t==None:
						tager = Tags()
						tager.content = lang
						tager.is_language = True;

						protag = ProjectTag()
						tager.put()
					else:
						tager = t
						tager.content = lang
						tager.is_language = True;

						tager.save()
					protag = ProjectTag()
					protag.tag = tager
					protag.project = project
					protag.put()
						
			
			if tags!="":
				for tag in tags:
					t = Tags.validate_tag(tag)
					if t==None:
						tager = Tags()
						tager.content = tag

						protag = ProjectTag()
						tager.put()
					else:
						tager = t
						tager.content = tag

						tager.save()

					protag = ProjectTag()
					protag.tag = tager
					protag.project = project
					protag.put()
			
						
			post_status = True
			self.redirect('/')
			
		except CapabilityDisabledError:
			post_status = False
			self.redirect('/?error=true')

class CodePost(AbstractRequestHandler):
	def _post(self):
		project = Projects.get_by_id(int(self.request.get('pid')))
		project.update_at = datetime.datetime.now()
		project.latest_update_user = self.appuser
		
		code = Codes()
		code.author = self.appuser
		# code.title = self.request.get('title')
		# code.content = self.request.get('code')
		# code.comment = self.request.get('comment')
		code.update_at = project.update_at
		
		memory = Memories()
		memory.author = self.appuser
		memory.title = self.request.get('title')
		memory.content = self.request.get('code')
		memory.comment = self.request.get('comment')
		memory.update_at = project.update_at
		
		# number = ""
		# while(1):
		# 	number = randstr(9)
		# 	if Codes.find_by_number(number) == None:
		# 		break
		# code.number = number
		
		procod = ProjectCode()
		codmem = CodeMemory()
		history = Histories()
		
		try:
			project.save()
			code.put()
			memory.put()
			
			history.author = project.author
			history.project = project
			history.action = "add_code"
			history.put()
		
			procod.code = code
			procod.project = project
			procod.put()
			
			codmem.code = code
			codmem.memory = memory
			codmem.put()
			
			post_status = True
			self.redirect('/project?pid='+self.request.get('pid'))
			
		except CapabilityDisabledError:
			post_status = False
			self.redirect('/?error=true')

class CodeUpdate(AbstractRequestHandler):
	def _post(self):
		project = Projects.get_by_id(int(self.request.get('pid')))
		project.update_at = datetime.datetime.now()
		project.latest_update_user = self.appuser
		
		code = Codes.get_by_id(int(self.request.get('cid')))
		# code.title = self.request.get('title')
		# code.content = self.request.get('code')
		# code.comment = self.request.get('comment')
		code.update_at = project.update_at
		
		memory = Memories()
		memory.author = self.appuser
		memory.title = self.request.get('title')
		memory.content = self.request.get('code')
		memory.comment = self.request.get('comment')
		memory.update_at = project.update_at
		
		# number = ""
		# while(1):
		# 	number = randstr(9)
		# 	if Codes.find_by_number(number) == None:
		# 		break
		# code.number = number
		
		procod = ProjectCode()
		codmem = CodeMemory()
		history = Histories()
		
		try:
			project.save()
			code.save()
			memory.put()
		
			history.author = project.author
			history.project = project
			history.action = "update_code"
			history.put()
			
		
			procod.code = code
			procod.project = project
			procod.put()
			
			codmem.code = code
			codmem.memory = memory
			codmem.put()
			
			post_status = True
			self.redirect('/project?pid='+self.request.get('pid'))
			
		except CapabilityDisabledError:
			post_status = False
			self.redirect('/?error=true')

		
class Registration(AbstractRequestHandler):
	def post(self):
		app_user = ApplicationUser()
		user = users.get_current_user()
		if user:
			#if users.get_current_user().email() == "isgroupsystem@gmail.com":
			#	app_user = ApplicationUser().all().filter("nickname = ", "admin").fetch(1)[0]
			#	app_user.user = users.get_current_user()
			#	app_user.put()
			if ApplicationUser.auth(user):
				self.redirect('/')
			elif app_user.registration(self.request,user):
				self.redirect('/')
			else:
				path = os.path.join(os.path.dirname(__file__), './templates/registration.html')
				template_values = {
									'current_user':user,
									'msgs':["認証に失敗しました．"]
									}
				self.response.out.write(template.render(path, template_values))
		else:
			url = users.create_login_url(self.request.uri)
			self.redirect(url)
	def get(self):
		user = users.get_current_user()
		if user:
			path = os.path.join(os.path.dirname(__file__), './templates/registration.html')
			template_values = {'current_user':user,'msgs':[]}
			self.response.out.write(template.render(path, template_values))
		else:
			url = users.create_login_url(self.request.uri)
			self.redirect(url)

class Mailer(webapp.RequestHandler):
	def post(self):
		addr = "mmiyajix@gmail.com"
		toaddr = "mmiyajix@gmail.com"
		subject = u"task finished"
		if self.request.get('to'):
			toaddr = self.request.get('to')
		if self.request.get('from'):
			addr = self.request.get('from')
		if self.request.get('sub'):
			subject = self.request.get('sub')
		body = self.request.get('body')
		if body != "":
			Config = {
				'Sender' : addr,
				'ToAddr' : toaddr,
				}
			mail.send_mail(sender = Config['Sender'], 
							to = Config['ToAddr'],
							subject = subject, 
							body = body,
							)
		

class Settings(AbstractRequestHandler):
	def _get(self):
		appuser = ApplicationUser.find_by_user(self.user)
		template_values = {
							'logout_url': users.create_logout_url(self.request.uri),
							'current_user':self.user,
							'appuser':appuser,
							'msgs':[],
							}
		path = os.path.join(os.path.dirname(__file__), './templates/settings.html')
		self.response.out.write(template.render(path, template_values))
			
	
	def _post(self):
		msgs = []
		tw_msgs = []
		if self.request.get('type') !="twitter":
			if self.request.get('nickname') =="":
				msgs.append("ユーザー名が入力されていません")
			elif self.appuser.nickname != self.request.get('nickname') and ApplicationUser.all().filter("nickname = ",self.request.get('nickname')).count() != 0:
				msgs.append("入力されたユーザー名は既に利用されています．別のユーザ名を入力してください．")
			elif not re.compile("^([A-Za-z0-9\'~+\-=_.]+)", re.I).search(self.request.get('nickname')):
				msgs.append("入力されたユーザー名がこの正規表現にあてはまりません．「^([A-Za-z0-9\'~+\-=_.]+)」")
			else:
				self.appuser.nickname = self.request.get('nickname')
				self.appuser.reload_time = int(self.request.get('reload_time'))
				self.appuser.img_url = self.request.get('img_url')
				self.appuser.put()
				msgs.append("変更しました")
		else:
			if self.request.get('tw_username') =="":
				tw_msgs.append("ユーザー名が入力されていません")
			if self.request.get('tw_password') =="":
				tw_msgs.append("パスワードが入力されていません")
			if self.request.get('tw_username') !="" and self.request.get('tw_password') !="":
				self.appuser.tw_username = self.request.get('tw_username')
				self.appuser.tw_password = self.request.get('tw_password')
				if self.request.get('tw_default_post_flg') == "true":
					self.appuser.tw_default_post_flg = True
				else:
					self.appuser.tw_default_post_flg = False
				self.appuser.put()
				tw_msgs.append("設定しました")
						
		template_values = {
							'logout_url': users.create_logout_url(self.request.uri),
							'current_user':self.user,
							'appuser':self.appuser,
							'msgs':msgs,
							'tw_msgs':tw_msgs
							}
		path = os.path.join(os.path.dirname(__file__), './templates/settings.html')
		self.response.out.write(template.render(path, template_values))
	
		
application = webapp.WSGIApplication(
                                     [('/', MainPage),
									  ('/registration', Registration),
									  ('/settings', Settings),
									  ('/makeproject', MakeProject),
									  ('/project', ProjectPage),
									  ('/tag', TagPage),
									  ('/isdl_editor', Isdl_Edit),
									  ('/inner_editor', Inner_Edit),
									  ('/mailer', Mailer),
									  ('/clustering', Clustering),
									  ('/fuzzy_clustering', Fuzzy),
									  ('/kmeans_clustering', Kmeans),
									  ('/preview', Preview),
									  ('/search', SearchPage),
									  ('/addcode', AddCode),
									  ('/editcode', EditCode),
									  ('/ppost', ProjectPost),
									  ('/cpost', CodePost),
									  ('/cupdate', CodeUpdate),
									 ],
                                     debug=True)

def randstr(n):
	alphabets = string.digits + string.letters
	return ''.join(random.choice(alphabets) for i in xrange(n))

def main():
	run_wsgi_app(application)

if __name__ == "__main__":
	main()