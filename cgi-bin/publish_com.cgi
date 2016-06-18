#!../venv/bin/python

import cgi,sys,os
import cgitb
cgitb.enable()

import json

import imp

import subprocess

loadUser = imp.load_source('loadUser','loadUser.cgi')
loadPages = imp.load_source('loadPages','loadPages.cgi')

pagesDir = "../assignments/"
alist = "/alist"

compExt = ".completed"
lock = ".lock"

gradeDir = "../grades/"

def changePublish():

        form = cgi.FieldStorage()

        course = form.getvalue("classID")
        page = form.getvalue("page")
        pub = form.getvalue("publish")

        user,admin,grading = loadUser.getUser()

        admin = admin.split(",")

        if course not in admin:
                sys.stdout.write(course)
                sys.stdout.write('<script type="text/javascript">alert("Not authorized for that course!");</script>')
                # insert logging of unauthorized entry here...
                quit()

        pageList = loadPages.loadPages(course)

        for i in range(0, len(pageList)):
                if pageList[i]["name"] == page:
                        pageList[i]["publish_com"] = pub
                        break

        with open(pagesDir + course + alist, 'w') as f:
                f.write(json.dumps(pageList))

if __name__ == '__main__':
        sys.stdout.write("Content-Type: text/html")
        sys.stdout.write("\n")
        sys.stdout.write("\n")
        changePublish()
