# coding:utf-8

# asc2wp ver 0.6.6
# This program request
# python 3.11.6
# python-wordpress-xmlrpc https://python-wordpress-xmlrpc.readthedocs.org
# asciidoctor http://asciidoctor.org
import distutils.spawn
import mimetypes
import os
import re
import subprocess
import sys
import time
from datetime import datetime

import yaml


class Asc2wp:
    """
    methods:
    asciidoctor_check
        + checks if asciidoctor is installed
    argv_check
        + checks if there is input supplied
    make_setting_file
        + will create a blank settings file for modification
    read_setting_file
        + will load the settings for transfer and file modification
    make_new_file
        + make a template file for
        you to edit or use for
        creation of new adoc files
    media_upload
        + takes a list of files that
        need submission and it
        will send them to wordppess
    basic_process
        + start the processing of the
        adoc files
    timezone
        + get the timezone from the
        sever to know when a document
        has been submitted
    printhelp
        + just to output the help
        info for the system
    post_type
        + check if post or page
        needed for creation in
        wordpress
    post
        + read and submit details
        for a post
    page
        + read and submit details
        for a page

    """

    def printhelp(self):
        """help details"""
        print(
            "Usage: asc2wp FILE...\n\n"
            + "To create config file\n"
            + "Usage: asc2wp init \n\n"
            + "To create Template file \n"
            + "Usage: asc2wp makefile\n\n\n"
            + "To upload multiple adoc's\n"
            + "Usage: asc2wp 2016-05-*.adoc\n\n"
            + "To upload multiple media files\n"
            + "Usage: asc2wp -m {image-files}\n\n"
        )
        return

    def asciidoctor_check(self):
        """
        check if Asciidoctor alreday installed to convert the adoc to html
        """
        if (distutils.spawn.find_executable("asciidoctor")) is None:
            print(
                '"Asciidoctor"　'
                + "does not exist. "
                + "Please install "
                + "Asciidoctor.\n"
                + "http://asciidoctor.org"
            )
            sys.exit(0)  # quit Python

    def argv_check(self):
        """
        check for command line arguments provided
        """
        if len(sys.argv[1:]) == 0:
            print("Error: Please input some options.")
            Asc2wp().printhelp()
            sys.exit(0)
        if sys.argv[1] == "-?":
            Asc2wp().printhelp()
            sys.exit(0)
        if sys.argv[1] == "--help":
            Asc2wp().printhelp()
            sys.exit(0)

    def make_setting_file(self):
        """
        check if file existd error else make an empty settings file
        """
        if os.path.exists("setting.yaml") is True:
            print('Error: Already exist "setting.yaml".')
            sys.exit(0)  # quit Python
        else:
            file_name = "setting.yaml"
            setting_file_content = (
                "url: http://example.com\n"
                + "xmlrpc_url: http://example.com/xmlrpc.php\n"
                + "username: \n"
                + "password: \n"
                + "remove_div: False\n"
                + "remove_p: False\n"
                + "remove_p_tableblock: False\n"
            )
            with open(file_name, "a") as setting_file:
                # Trying to create a new file
                setting_file.write(setting_file_content)
            print(
                "Created setting file "
                + '"setting.yaml".'
                + "Please input your "
                + "Wordpress's information."
            )

    def read_setting_file(self):
        """
        read the settings file and setup the variables
        NOTE: not the best as password loaded as a global :(
        should also allow for input if not saved in settings file
        """
        setting_yaml_file = "setting.yaml"

        if os.path.exists(setting_yaml_file) is False:
            print("Error: Setting file " + "does not exist ")
            sys.exit(0)  # quit Python
        else:
            with open(setting_yaml_file, "r") as f:
                data = yaml.safe_load(f)
                global xmlrpc_url
                xmlrpc_url = data["xmlrpc_url"]
                global username
                username = data["username"]
                global password
                password = data["password"]
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

    def make_new_file(self):
        """
        create a new ADOC file for editing.
        """
        print("Create new template file")
        while True:
            file_type = input(
                'Which file type? (Please type "post" or "page"): '
            ).lower()
            if file_type == "post":
                break
            elif file_type == "page":
                break
        file_name = (
            input("Enter name of text" + " file (No need for the extension): ")
            + ".adoc"
        )
        if file_type == "post":
            try:
                new_file_content = (
                    ":wp_type: post \n"
                    + ":wp_status: publish\n"
                    + ":wp_date: \n"
                    + ":wp_modified: \n"
                    + ":wp_id: \n"
                    + ":wp_title: \n"
                    + ":wp_slug: \n"
                    + ":wp_category: \n"
                    + ":wp_tag: \n"
                    + ":wp_excerpt: \n"
                    + ":wp_thumbnail: \n"
                    + "\n\n//asciidoc contents"
                )
                with open(file_name, "a") as new_file:
                    # Trying to create a new file or open one
                    new_file.write(new_file_content)

            except:
                print("Error")
                sys.exit(0)  # quit Python
        elif file_type == "page":
            try:
                new_file_content = (
                    ":wp_type: page \n"
                    + ":wp_status: publish\n"
                    + ":wp_date: \n"
                    + ":wp_modified: \n"
                    + ":wp_id: \n"
                    + ":wp_title: \n"
                    + ":wp_slug: \n"
                    + ":wp_thumbnail: \n"
                    + "\n\n//asciidoc contents"
                )
                with open(file_name, "a") as new_file:
                    # Trying to create a new file or open one
                    new_file.write(new_file_content)
            except:
                print("Error")
                sys.exit(0)  # quit Python

        print("Created : " + file_name)

    def media_upload(self):
        """
        upload media files as input as command line arguments
        """
        print("Media Upload")
        from wordpress_xmlrpc import Client, WordPressPost
        from wordpress_xmlrpc.compat import xmlrpc_client
        from wordpress_xmlrpc.methods import media, posts

        client = Client(xmlrpc_url, username, password)
        if len(param_list[2:]) == 0:
            print("Error: Please select Uploads file")
            sys.exit(0)
        else:
            for f in param_list[2:]:
                filepath = os.path.abspath(f)
                filename = os.path.basename(filepath.strip())
                dirname = os.path.dirname(filepath.strip())
                # prepare metadata
                data = {"name": filename, "type": mimetypes.guess_type(filename)[0]}
                # read the binary file and let the XMLRPC library encode it into base64
                with open(filepath.strip(), "rb") as img:
                    data["bits"] = xmlrpc_client.Binary(img.read())
                response = client.call(media.UploadFile(data))
                attachment_id = response["id"]
                media_info = client.call(media.GetMediaItem(attachment_id))
                media_filename = os.path.basename(media_info.link.strip())
                print(
                    "==========================\n"
                    + "Attachment ID : "
                    + attachment_id
                    + "\nFile name : "
                    + media_filename
                    + "\nFile url : "
                    + media_info.link
                )

    def basic_process(self):
        """
        process ADOC file to html then using bash sed to build a file
        for transfer to wordpress
        NOTE: should be done in python fully after HTML file is created
        and it should return it to the process that should call it
        not by using a global variable
        """
        global filepath
        filepath = os.path.abspath(param)
        filename = os.path.basename(filepath.strip())
        dirname = os.path.dirname(filepath.strip())

        # error
        if os.path.isdir(filepath) is True:
            print("Error:Is a directory")
            sys.exit(0)  # quit Python
        else:
            # html file outpu dir
            dirname_output = dirname + "/output/"

            # asciidoc to Html
            cmd = (
                "asciidoctor -D "
                + dirname_output
                + " -s "
                + filepath
                + " -o "
                + filename
                + ".html"
            )
            subprocess.call(cmd, shell=True)

            cmd1 = "cat -s " + dirname_output + filename + ".html"

            if remove_div is True:
                cmd1 = cmd1 + " | sed -e 's/<div [^>]*>//g' | sed -e 's/<\/div>//g'"
            if remove_p is True:
                cmd1 = (
                    cmd1
                    + " | sed -e 's/<p>//g' | sed -e 's/<p [^>]*>//g' | sed -e 's/<\/p>//g'"
                )
            if remove_p_tableblock is True:
                cmd1 = (
                    cmd1
                    + " | sed -e 's/<p "
                    + 'class=\\"tableblock\\">\(.*\)<\/p>/\\1/g\''
                )
            cmd1 = cmd1 + " | sed '/^$/d'"

            global html
            html = subprocess.check_output(cmd1, shell=True)

            # get post info from asciidoc file
            with open(filepath, "r") as asc_file_read:
                global asc_file_read_str
                asc_file_read_str = asc_file_read.read()

    def timezone(self):
        """
        get the wprdpress timezone to adjust the local time
        to the wordpress time.
        """
        from wordpress_xmlrpc import Client, WordPressOption
        from wordpress_xmlrpc.methods import options

        client = Client(xmlrpc_url, username, password)
        timezone = client.call(options.GetOptions("time_zone"))
        timezone_ = timezone[0]
        # print str(timezone_)
        timezone__ = re.search(r'time_zone="(.+)"', str(timezone_)).group(1).strip()
        global timezone___
        timezone___ = float(timezone__)

    def post_type(self):
        """
        check file for wp_type
        """
        global post_type_
        post_type_ = re.search(":wp_type:((.*)|\n)", asc_file_read_str).group(1).strip()
        if not post_type_:
            print('Error: Please set "post" or "page"' + '":wp_type: "')
            sys.exit(0)  # quit Python

    def post(self):
        """
        check file for wp details
        """
        # get id
        post_id = re.search(":wp_id:((.*)|\n)", asc_file_read_str).group(1).strip()

        # get status
        post_status = re.search(":wp_status:((.*)|\n)", asc_file_read_str)

        # get title
        post_title = re.search(":wp_title:((.*)|\n)", asc_file_read_str)

        # get slug
        post_slug = re.search(":wp_slug:((.*)|\n)", asc_file_read_str)

        # get category
        post_category = re.search(":wp_category:((.*)|\n)", asc_file_read_str)
        post_category_str = post_category.group(1).strip().split(", ")

        if len(post_category_str) == 0:
            post_category_str = []
        elif post_category.group(1).strip() == "":
            post_category_str = []
        elif len(post_category_str) == 1:
            post_category_str = (post_category.group(1).strip(),)

        # get tag
        post_tag = re.search(":wp_tag:((.*)|\n)", asc_file_read_str)
        post_tag_str = post_tag.group(1).strip().split(", ")

        if len(post_tag_str) == 0:
            post_tag_str = []
        elif post_tag.group(1).strip() == "":
            post_tag_str = []
        elif len(post_tag_str) == 1:
            post_tag_str = (post_tag.group(1).strip(),)

        # get excerpt
        post_excerpt = re.search(":wp_excerpt:((.*)|\n)", asc_file_read_str)

        # get thumbnail
        post_thumbnail = re.search(":wp_thumbnail:((.*)|\n)", asc_file_read_str)

        # post to wordpress
        from wordpress_xmlrpc import Client, WordPressPost
        from wordpress_xmlrpc.methods import posts

        client = Client(xmlrpc_url, username, password)
        post = WordPressPost()

        date_ = datetime.now()
        # id New or Edit
        if not post_id:
            post.date = date_.strftime("%s")
            post.id = client.call(posts.NewPost(post))
            mode = "New"
            asc_file_re = re.sub(
                r":wp_id:((.*)|\n)", ":wp_id: " + post.id, asc_file_read_str
            )
            with open(filepath, "w") as asc_file_write:
                asc_file_write.write(asc_file_re)
        else:
            post.date_modified = date_.strftime("%s")
            post.id = post_id
            mode = "Edit"

        post.post_status = post_status.group(1).strip()

        try:
            post.title = post_title.group(1).strip()
        except:
            print("Title does not exist")

        try:
            post.slug = post_slug.group(1).strip()
        except:
            print("Slug does not exist")

        post.content = html

        try:
            post.excerpt = post_excerpt.group(1).strip()
        except:
            post.excerpt = ""

        post.terms_names = {
            "category": post_category_str,
            "post_tag": post_tag_str,
        }

        try:
            post.thumbnail = post_thumbnail.group(1).strip()
        except:
            post.thumbnail = ""

        client.call(posts.EditPost(post.id, post))

        post_info = client.call(posts.GetPost(post.id, post))

        # get post info from wordpress
        with open(filepath, "r") as asc_file_read_slug:
            asc_file_read_slug_str = asc_file_read_slug.read()

        if post_info:
            asc_file_read_slug_str = re.sub(
                r":wp_slug:((.*)|\n)",
                ":wp_slug: " + post_info.slug,
                asc_file_read_slug_str,
            )
            if mode == "New":
                new_date = int(post_info.date.strftime("%s"))
                +(timezone___ * 60 * 60)
                new_date = datetime.fromtimestamp(new_date).strftime(
                    "%Y-%m-%d %H:%M:%S"
                )
                asc_file_read_slug_str = re.sub(
                    r":wp_date:((.*)|\n)",
                    ":wp_date: " + new_date,
                    asc_file_read_slug_str,
                )
            elif mode == "Edit":
                edit_date = int(post_info.date_modified.strftime("%s"))
                +(timezone___ * 60 * 60)
                edit_date = datetime.fromtimestamp(edit_date).strftime(
                    "%Y-%m-%d %H:%M:%S"
                )
                asc_file_read_slug_str = re.sub(
                    r":wp_modified:((.*)|\n)",
                    ":wp_modified: " + edit_date,
                    asc_file_read_slug_str,
                )
            with open(filepath, "w") as asc_file_re_slug_write:
                asc_file_re_slug_write.write(asc_file_read_slug_str)

        print(
            "==========================\n"
            + mode
            + " Post ID: "
            + post.id
            + " \nStatus: "
            + post.post_status
            + "\nTitle: "
            + post.title
            + "\nSlug: "
            + post_info.slug
            + "\nCategory: "
            + post_category.group(1).strip()
            + "\nTag: "
            + post_tag.group(1).strip()
            + "\n"
        )

    def page(self):
        # get id
        page_id = re.search(":wp_id:((.*)|\n)", asc_file_read_str).group(1).strip()

        # get page status
        page_status = (
            re.search(":wp_status:((.*)|\n)", asc_file_read_str).group(1).strip()
        )

        # get title
        page_title = (
            re.search(":wp_title:((.*)|\n)", asc_file_read_str).group(1).strip()
        )

        # get slug
        page_slug = re.search(":wp_slug:((.*)|\n)", asc_file_read_str).group(1).strip()

        page_thumbnail = (
            re.search(":wp_thumbnail:((.*)|\n)", asc_file_read_str).group(1).strip()
        )

        # post to wordpress
        from wordpress_xmlrpc import Client, WordPressPage, WordPressPost
        from wordpress_xmlrpc.methods import posts

        client = Client(xmlrpc_url, username, password)
        page = WordPressPage()
        post = WordPressPost()

        # id New or Edit
        if not page_id:
            page.date = datetime.now().strftime("%s")
            page.id = client.call(posts.NewPost(page))
            mode = "New"
            asc_file_re = re.sub(
                r":wp_id:((.*)|\n)", ":wp_id: " + page.id, asc_file_read_str
            )
            with open(filepath, "w") as asc_file_write:
                asc_file_write.write(asc_file_re)
        else:
            page.date_modified = datetime.now().strftime("%s")
            page.id = page_id
            mode = "Edit"

        # page status
        page.post_status = page_status

        # page title
        try:
            page.title = page_title
        except:
            print("Title does not exist")

        # page slug
        try:
            page.slug = page_slug
        except:
            print("Slug does not exist")

        # page content
        page.content = html

        # page thumbnail
        try:
            page.thumbnail = page_thumbnail
        except:
            page.thumbnail = ""

        client.call(posts.EditPost(page.id, page))

        page_info = client.call(posts.GetPost(page.id, post))

        # get post info from wordpress
        with open(filepath, "r") as asc_file_read_slug:
            asc_file_read_slug_str = asc_file_read_slug.read()

        if page_info:
            asc_file_read_slug_str = re.sub(
                r":wp_slug:((.*)|\n)",
                ":wp_slug: " + page_info.slug,
                asc_file_read_slug_str,
            )
            if mode == "New":
                new_date = int(page_info.date.strftime("%s"))
                +(timezone___ * 60 * 60)
                new_date = datetime.fromtimestamp(new_date).strftime(
                    "%Y-%m-%d %H:%M:%S"
                )
                asc_file_read_slug_str_ = re.sub(
                    r":wp_date:((.*)|\n)",
                    ":wp_date: " + new_date,
                    asc_file_read_slug_str,
                )
            elif mode == "Edit":
                edit_date = int(page_info.date_modified.strftime("%s")) + (
                    timezone___ * 60 * 60
                )
                edit_date = datetime.fromtimestamp(edit_date).strftime(
                    "%Y-%m-%d %H:%M:%S"
                )
                asc_file_read_slug_str_ = re.sub(
                    r":wp_modified:((.*)|\n)",
                    ":wp_modified: " + edit_date,
                    asc_file_read_slug_str,
                )
            with open(filepath, "w") as asc_file_re_slug_write:
                asc_file_re_slug_write.write(asc_file_read_slug_str_)

        print(
            "==========================\n"
            + mode
            + " Page ID: "
            + page.id
            + " \nStatus: "
            + page.post_status
            + "\nTitle: "
            + page.title
            + "\nSlug: "
            + page_info.slug
            + "\n"
        )


if __name__ == "__main__":
    # Main process

    Asc2wp().asciidoctor_check()
    Asc2wp().argv_check()
    post_type_ = "not set"
    global param_list
    param_list = sys.argv
    global param
    for param in param_list[1:]:
        if param == "init":
            Asc2wp().make_setting_file()
            sys.exit(0)
        elif param == "makefile":
            Asc2wp().make_new_file()
            sys.exit(0)
        elif param == "-m":
            Asc2wp().read_setting_file()
            Asc2wp().media_upload()
            sys.exit(0)
        else:
            Asc2wp().read_setting_file()
            Asc2wp().basic_process()
            Asc2wp().timezone()
            Asc2wp().post_type()
            if post_type_ == "post":
                Asc2wp().post()
                sys.exit(0)
            elif post_type_ == "page":
                Asc2wp().page()
                sys.exit(0)
