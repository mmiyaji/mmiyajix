#!/usr/bin/env python
# encoding: utf-8
"""
filer.py

Created by Masahiro MIYAJI on 2011-05-29.
Copyright (c) 2011 ISDL. All rights reserved.
"""
from google.appengine.ext import db
from model import *
from getimageinfo import *
class PostData(db.Model):
	appuser =  db.ReferenceProperty(ApplicationUser,
									collection_name='upload_by')
	comment  = db.StringProperty(multiline=True, default="")
	filename = db.StringProperty(multiline=False, default="")
	filemimetype = db.StringProperty(multiline=False)
	create_at = db.DateTimeProperty(auto_now_add=True)
	update_at = db.DateTimeProperty(auto_now=True)
	is_image = db.BooleanProperty(default=False)
	down_lock = db.BooleanProperty(default=False)
	down_user = db.StringProperty(default="", multiline=False)
	down_pass = db.StringProperty(default="", multiline=False)
	size = db.IntegerProperty()
	downcount  = db.IntegerProperty(default=0)
	width = db.IntegerProperty()
	height = db.IntegerProperty()
	img_url = db.StringProperty(default="")	
	
	def en_filename(self):
		import cgi
		return cgi.escape(self.filename)
	
	@staticmethod
	def download_data(fid=""):
		if fid:
			postdata = db.get(fid)
			postdata.downcount += 1
			postdata.save()
			blobs = ""
			try:
				if memcache.get(str(fid)):
					blobs = memcache.get(str(fid))
				else:
					blobs = PostDataChunk.get_by_master(master=postdata.key())
					memcache.add(str(fid), blobs)
			except:
				pass
			return blobs,postdata.filemimetype
		else:
			return None

	@staticmethod
	def upload_data(filedata=None,appuser=None,comment="",filename="",filemimetype="",passwd=""):
		if True:
			postdata = PostData()
			postdata.comment = comment
			postdata.filename = filename
			postdata.filemimetype = filemimetype
			postdata.appuser = appuser
			postdata.size = len(filedata)
			bin = db.Blob(filedata)
			content_type, width, height = getImageInfo(bin)
			postdata.width = width
			postdata.height = height
			if width!=-1 or height!=-1:
				postdata.is_image = True
			if passwd!="":
				postdata.down_lock = True
				postdata.down_pass = passwd
			postdata.put()
			for i in xrange( len(filedata) / 500000 + 1):
				chunk = PostDataChunk()
				chunk.master = postdata.key()
				chunk.seq = i
				chunk.chunk = db.Blob(filedata[i*500000:(i+1)*500000 ])
				chunk.put()
				
			entry = Entry()
			entry.title = filename
			entry.types = "file"
			entry.is_draft = False
			entry.content = comment
			entry.full_content = comment
			entry.save()
			entry.relation.append(postdata.key())
			entry.save()
			return postdata
			
class PostDataChunk(db.Model):
	master= db.ReferenceProperty(PostData)
	seq = db.IntegerProperty()
	chunk = db.BlobProperty()
	@staticmethod
	def get_by_master(master=None):
		result = ""
		if master:
			query = PostDataChunk.all().order('-seq').filter('master = ',master)
			for i in query:
				result += i.chunk
		return result
	