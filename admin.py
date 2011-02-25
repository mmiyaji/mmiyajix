#!/usr/bin/env python
# encoding: utf-8
"""
admin.py

Created by Masahiro MIYAJI on 2011-02-23.
Copyright (c) 2011 ISDL. All rights reserved.
"""
import os,urllib,random,datetime,logging,re
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
from url_handler import *

class ManagePage(ModifyRequestHandler):
	def _get(self):
		entries,entry_count = Entry.get_entries(span=5,page=0)
		template_values = None
		template_values = {
				'now':self.now,
				'user':self.user,
				'appuser':self.appuser,
				'application':self.application,
				'entries':entries,
				'entry_count':entry_count,
				'url': self.url,
			}
		path = os.path.join(os.path.dirname(__file__), './templates/base/manage.html')
		self.response.out.write(template.render(path, template_values))	

class EditPage(ModifyRequestHandler):
	def _get(self):
		template_values = None
		template_values = {
				'now':self.now,
				'user':self.user,
				'appuser':self.appuser,
				'application':self.application,
				'url': self.url,
			}
		path = os.path.join(os.path.dirname(__file__), './templates/base/edit.html')
		self.response.out.write(template.render(path, template_values))	
		
	def _post(self):
		if True:
			if self.request.get("entry_id"):
				entry = Entry.get_by_id(int(self.request.get("entry_id")))
			else:
				entry = Entry()
			entry.appuser = self.appuser
			entry.title = self.request.get("title")
			content = self.request.get("content")
			p = re.compile(r'<.*?>')
			content = p.sub('', content)
			if len(content)>500:
				content = content[0:500]
			n = re.compile(r'\n')
			content = n.sub('<br />', content)
			entry.content = content
			entry.full_content = self.request.get("full_content")
			entry.save()
		self.redirect("/")
	
class EditorPage(webapp.RequestHandler):
	def get(self):
		template_values = None
		path = os.path.join(os.path.dirname(__file__), './templates/base/editor_frame.html')
		self.response.out.write(template.render(path, template_values))	

class CreateAppPage(BasicAuthentication):
	def _get(self):
		if self.appuser:
			template_values = None
			template_values = {
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
