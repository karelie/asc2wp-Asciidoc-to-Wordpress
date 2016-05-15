# coding:utf-8

#asc2wp ver 0.6.6
#This program request
#python 2.x
#python-wordpress-xmlrpc https://python-wordpress-xmlrpc.readthedocs.org
#asciidoctor http://asciidoctor.org
import distutils.spawn
import yaml
import subprocess
import re
import sys
import os
import time
import mimetypes
from datetime import datetime

class asc2wp:

	def asciidoctor_check():
		if (distutils.spawn.find_executable('asciidoctor')) == None:
			print '"Asciidoctor"　dose not exist. Please install Asciidoctor.\nhttp://asciidoctor.org'
			sys.exit(0) # quit Python
			
	def argv_check():
		if len(sys.argv[1:]) == 0:
			print 'Error: Please input some options.'
			sys.exit(0) # quit Python

	def make_setting_file():
		if os.path.exists('setting.yaml') == True:
			print 'Error: Already exist "setting.yaml".'
			sys.exit(0) # quit Python
		else:
			file_name = 'setting.yaml'
			setting_file_content = "url: \nxmlrpc_url: \nusername: \npassword: \nremove_div: False\nremove_p: False\nremove_p_tableblock: False\n"
			setting_file = open(file_name,'a')   # Trying to create a new file or open one
			setting_file.write(setting_file_content)
			setting_file.close()
			print 'Creat setting file "setting.yaml". Plese write your Wordpress\'s informations.'

	def read_setting_file():
		setting_yaml_file = 'setting.yaml'

		if os.path.exists(setting_yaml_file) == False:
			print "Error: Setting file's dose not exist "
			sys.exit(0) # quit Python
		else:
			f = open(setting_yaml_file, 'r')
			data = yaml.load(f) 
			f.close()
			global xmlrpc_url
			xmlrpc_url = data['xmlrpc_url'] 
			global username
			username = data['username'] 
			global password
			password = data['password'] 
			global remove_div
			try:
				remove_div = data["remove_div"]
			except KeyError:
				remove_div = False
			global remove_p
			try:
				remove_p = data["remove_p"]
			except KeyError:
				remove_p = False
			global remove_p_tableblock
			try:
				remove_p_tableblock = data["remove_p_tableblock"]
			except KeyError:
				remove_p_tableblock = False

	def make_new_file():
		print('Creat new template file')
		while True:
			file_type = raw_input('Wich file type? (Please type "post" or "page"): ').lower()
			if file_type == "post":
				break	
			elif file_type == "page":
				break
		file_name = raw_input('Enter name of text file (Not need input the extension): ') + '.adoc'
		if file_type == "post":
			try:
				new_file_content = ":wp_type: post \n:wp_status: publish\n:wp_date: \n:wp_modified: \n:wp_id: \n:wp_title: \n:wp_slug: \n:wp_category: \n:wp_tag: \n:wp_excerpt: \n:wp_thumbnail: \n\n\n//asciidoc contents"
				new_file = open(file_name,'a')   # Trying to create a new file or open one
				new_file.write(new_file_content)
				new_file.close()
			except:
				print('Error')
				sys.exit(0) # quit Python
		elif file_type == "page":
			try:
				new_file_content = ":wp_type: page \n:wp_status: publish\n:wp_date: \n:wp_modified: \n:wp_id: \n:wp_title: \n:wp_slug: \n:wp_thumbnail: \n\n\n//asciidoc contents"
				new_file = open(file_name,'a')   # Trying to create a new file or open one
				new_file.write(new_file_content)
				new_file.close()
			except:
				print('Error')
				sys.exit(0) # quit Python

		print "Created : " + file_name


	def media_upload():
		print 'Media Upload'
		from wordpress_xmlrpc import Client, WordPressPost
		from wordpress_xmlrpc.compat import xmlrpc_client
		from wordpress_xmlrpc.methods import media, posts

		client = Client(xmlrpc_url, username, password)
		if len(param_list[2:]) == 0:
			print "Error: Please select Uploads file"
			sys.exit(0)
		else:
			for f in param_list[2:]:
				filepath = os.path.abspath(f)
				filename = os.path.basename(filepath.strip())
				dirname = os.path.dirname(filepath.strip())
			# prepare metadata
				data = {
			        'name': filename,
			        'type': mimetypes.guess_type(filename)[0]
				}
			# read the binary file and let the XMLRPC library encode it into base64
				with open(filepath.strip(), 'rb') as img:
			       		data['bits'] = xmlrpc_client.Binary(img.read())
				response = client.call(media.UploadFile(data))
				attachment_id = response['id']
				media_info = client.call(media.GetMediaItem(attachment_id))
				media_filename = os.path.basename(media_info.link.strip())
				print '==========================\n' + 'Attachment ID : ' + attachment_id + '\nFile name : ' + media_filename + '\nFile url : ' + media_info.link


	def basic_process():
		global filepath
		filepath = os.path.abspath(param)
		filename = os.path.basename(filepath.strip())
		dirname = os.path.dirname(filepath.strip())

		#error
		if os.path.isdir(filepath) == True:
			print "Error:Is a directory"
			sys.exit(0) # quit Python
		else:
			#html file outpu dir
			dirname_output = dirname + "/output/"

			#asciidoc to Html
			cmd = "asciidoctor -D " + dirname_output + " -s " + filepath + " -o " + filename + ".html"
			# cmd = "asciidoc -s -o " + dirname_output + filename + ".html " + filepath
			# print cmd
			subprocess.call( cmd, shell=True  )

			cmd1 = "cat -s " + dirname_output + filename + ".html"

			if remove_div == True:
				cmd1 = cmd1 + " | sed -e 's/<div [^>]*>//g' | sed -e 's/<\/div>//g'"
			if remove_p == True:
				cmd1 = cmd1 + " | sed -e 's/<p>//g' | sed -e 's/<p [^>]*>//g' | sed -e 's/<\/p>//g'"
			if remove_p_tableblock == True:
				cmd1 = cmd1 + " | sed -e 's/<p class=\\\"tableblock\\\">\(.*\)<\/p>/\\1/g'"
			cmd1 = cmd1 + " | sed '/^$/d'"

			global html
			html = subprocess.check_output( cmd1, shell=True  )

			#get post info from asciidoc file
			asc_file_read = open(filepath, 'r')
			global asc_file_read_str
			asc_file_read_str = asc_file_read.read()

	def timezone():
		from wordpress_xmlrpc import Client, WordPressOption 
		from wordpress_xmlrpc.methods import options
		client = Client(xmlrpc_url, username, password)
		timezone = client.call(options.GetOptions('time_zone'))
		timezone_ = timezone[0]
		# print str(timezone_)
		timezone__ = re.search(r'time_zone="(.+)"', str(timezone_)).group(1).strip()
		global timezone___
		timezone___ = float(timezone__)

	def post_type():
		global post_type_
		post_type_ = re.search(':wp_type:((.*)|\n)', asc_file_read_str).group(1).strip()
		if not post_type_:
			print 'Error: Please set "post" or "page" with ":wp_type: "'
			sys.exit(0) # quit Python



	def post():
		#get id
		post_id = re.search(':wp_id:((.*)|\n)', asc_file_read_str).group(1).strip()

		#get status
		post_status = re.search(':wp_status:((.*)|\n)', asc_file_read_str)

		#get title
		post_title = re.search(':wp_title:((.*)|\n)', asc_file_read_str)

		#get slug
		post_slug = re.search(':wp_slug:((.*)|\n)', asc_file_read_str)

		#get category
		post_category = re.search(':wp_category:((.*)|\n)', asc_file_read_str)
		post_category_str = post_category.group(1).strip().split(", ")

		if len(post_category_str) == 0:
			post_category_str = []
		elif post_category.group(1).strip() == '':
			post_category_str = []
		elif len(post_category_str) == 1:
			post_category_str = post_category.group(1).strip(),

		#get tag
		post_tag = re.search(':wp_tag:((.*)|\n)', asc_file_read_str) 
		post_tag_str = post_tag.group(1).strip().split(", ")

		if len(post_tag_str) == 0:
			post_tag_str = []
		elif post_tag.group(1).strip() == '':
			post_tag_str = []
		elif len(post_tag_str) == 1:
			post_tag_str = post_tag.group(1).strip(),

		#get excerpt
		post_excerpt = re.search(':wp_excerpt:((.*)|\n)', asc_file_read_str)

		#get thumbnail
		post_thumbnail = re.search(':wp_thumbnail:((.*)|\n)', asc_file_read_str)

		#post to wordpress
		from wordpress_xmlrpc import Client, WordPressPost
		from wordpress_xmlrpc.methods import posts
		client = Client(xmlrpc_url, username, password)
		post = WordPressPost()


		date_ = datetime.now()
		#id New or Edit
		if not post_id:
			post.date = date_.strftime("%s")
			post.id = client.call(posts.NewPost(post))
			mode = "New"
			asc_file_re = re.sub(r':wp_id:((.*)|\n)', ':wp_id: ' + post.id , asc_file_read_str)
			asc_file_write = open(filepath, 'w')
			try:
				asc_file_write.write( asc_file_re )
			finally:
				asc_file_write.close()
		else:
			post.date_modified = date_.strftime("%s")
			post.id = post_id
			mode = "Edit"

		post.post_status = post_status.group(1).strip()

		try:
			post.title = post_title.group(1).strip()
		except:
			print 'Title is not exist'

		try:
			post.slug =  post_slug.group(1).strip()
		except:
			print 'Slug is not exist'

		post.content =  html

		try:
			post.excerpt = post_excerpt.group(1).strip()
		except:
			post.excerpt =  ''

		post.terms_names = {
		        'category': post_category_str,
		        'post_tag': post_tag_str,
		}

		try:
			post.thumbnail = post_thumbnail.group(1).strip()
		except:
			post.thumbnail =  ''

		client.call(posts.EditPost(post.id, post))

		post_info = client.call(posts.GetPost(post.id, post))


		#get post info from wordpress
		asc_file_read_slug = open(filepath, 'r')
		asc_file_read_slug_str = asc_file_read_slug.read()

		if post_info:
			asc_file_read_slug_str = re.sub(r':wp_slug:((.*)|\n)', ':wp_slug: ' + post_info.slug, asc_file_read_slug_str)
			if mode == "New":
				new_date = int(post_info.date.strftime("%s"))+(timezone___*60*60)
				new_date = datetime.fromtimestamp(new_date).strftime("%Y-%m-%d %H:%M:%S")
				asc_file_read_slug_str = re.sub(r':wp_date:((.*)|\n)', ':wp_date: ' + new_date, asc_file_read_slug_str)
			elif mode == "Edit":
				edit_date = int(post_info.date_modified.strftime("%s"))+(timezone___*60*60)
				edit_date = datetime.fromtimestamp(edit_date).strftime("%Y-%m-%d %H:%M:%S")
				asc_file_read_slug_str = re.sub(r':wp_modified:((.*)|\n)', ':wp_modified: ' + edit_date, asc_file_read_slug_str)
			asc_file_re_slug_write = open(filepath, 'w')
			try:
				asc_file_re_slug_write.write( asc_file_read_slug_str )
			finally:
				asc_file_re_slug_write.close()

		print '==========================\n' + mode + ' Post ID: ' + post.id + ' \nStatus: ' + post.post_status + '\nTitle: ' + post.title + '\nSlug: ' + post_info.slug + '\nCategory: ' + post_category.group(1).strip() + '\nTag: ' + post_tag.group(1).strip() + '\n'


	def page():

		#get id
		page_id = re.search(':wp_id:((.*)|\n)', asc_file_read_str).group(1).strip()

		#get page status
		page_status = re.search(':wp_status:((.*)|\n)', asc_file_read_str).group(1).strip()

		#get title
		page_title = re.search(':wp_title:((.*)|\n)', asc_file_read_str).group(1).strip()

		#get slug
		page_slug = re.search(':wp_slug:((.*)|\n)', asc_file_read_str).group(1).strip()

		page_thumbnail = re.search(':wp_thumbnail:((.*)|\n)', asc_file_read_str).group(1).strip()

		#post to wordpress
		from wordpress_xmlrpc import Client, WordPressPage, WordPressPost
		from wordpress_xmlrpc.methods import posts
		client = Client(xmlrpc_url, username, password)
		page = WordPressPage()
		post = WordPressPost()

		#id New or Edit
		if not page_id:
			page.date = datetime.now().strftime("%s")
			page.id = client.call(posts.NewPost(page))
			mode = "New"
			asc_file_re = re.sub(r':wp_id:((.*)|\n)', ':wp_id: ' + page.id, asc_file_read_str)
			asc_file_write = open(filepath, 'w')
			try:
				asc_file_write.write( asc_file_re )
			finally:
				asc_file_write.close()
		else:
			page.date_modified = datetime.now().strftime("%s")
			page.id = page_id
			mode = "Edit"

		#page status
		page.post_status = page_status

		#page title
		try:
			page.title = page_title
		except:
			print 'Title is not exist'

		#page slug
		try:
			page.slug =  page_slug
		except:
			print 'Slug is not exist'
	 
		#page content
		page.content =  html

		#page thumbnail
		try:
			page.thumbnail = page_thumbnail
		except:
			page.thumbnail =  ''

		client.call(posts.EditPost(page.id, page))

		page_info = client.call(posts.GetPost(page.id, post))

		#get post info from wordpress
		asc_file_read_slug = open(filepath, 'r')
		asc_file_read_slug_str = asc_file_read_slug.read()

		if page_info:
			asc_file_read_slug_str = re.sub(r':wp_slug:((.*)|\n)', ':wp_slug: ' + page_info.slug, asc_file_read_slug_str)
			if mode == "New":
				new_date = int(page_info.date.strftime("%s"))+(timezone___*60*60)
				new_date = datetime.fromtimestamp(new_date).strftime("%Y-%m-%d %H:%M:%S")
				asc_file_read_slug_str_ = re.sub(r':wp_date:((.*)|\n)', ':wp_date: ' + new_date, asc_file_read_slug_str)
			elif mode == "Edit":
				edit_date = int(page_info.date_modified.strftime("%s"))+(timezone___*60*60)
				edit_date = datetime.fromtimestamp(edit_date).strftime("%Y-%m-%d %H:%M:%S")
				asc_file_read_slug_str_ = re.sub(r':wp_modified:((.*)|\n)', ':wp_modified: ' + edit_date, asc_file_read_slug_str)
			asc_file_re_slug_write = open(filepath, 'w')
			try:
				asc_file_re_slug_write.write( asc_file_read_slug_str_ )
			finally:
				asc_file_re_slug_write.close()

		print '==========================\n' + mode + ' Page ID: ' + page.id + ' \nStatus: ' + page.post_status + '\nTitle: ' + page.title + '\nSlug: ' + page_info.slug + '\n'


	# Main process
	asciidoctor_check()
	argv_check()
	global param_list
	param_list = sys.argv
	global param
	for param in param_list[1:] :
		if param == 'init':
			make_setting_file()
			sys.exit(0)
		elif param == 'makefile':
			make_new_file()
			sys.exit(0)
		elif param == '-m':
			read_setting_file()
			media_upload()
			sys.exit(0)
		else:
			read_setting_file()
			basic_process()
			timezone()
			post_type()
			if post_type_ == 'post':
				post()
				sys.exit(0)
			elif post_type_ == 'page':
				page()
				sys.exit(0)
