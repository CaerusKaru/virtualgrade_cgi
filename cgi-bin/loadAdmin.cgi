#!../venv/bin/python

import cgi,sys,os
import cgitb
cgitb.enable()

import json

import imp

import subprocess

loadUser = imp.load_source('loadUser','loadUser.cgi')

dirPath = "/g/" # or /comp/ for live version
tempInter = "/2016s" # remove for live version
gradingPath = "/grading/"

dirOnly = "/*/"

assignPath = "../assignments/"

inpExt = ".inprogress"
compExt = ".completed"

options = { "create":"Create/Import","delete":"Delete","publish":"Publish","export":"Export",
                "stats":"Statistics", "assign":"Assign Graders" }

def getAdmin():

        form = cgi.FieldStorage()

        course = form.getvalue("classID")

        user,admin,grading = loadUser.getUser()

        admin = admin.split(",")

        if course not in admin:
                sys.stdout.write('<script type="text/javascript">alert("Not authorized for that course!");</script>')
                # insert logging of unauthorized entry here...
                quit()

        insert = '<div id="admin">'

        insert += '<ul>'

        for key, value in options.items():
                insert += '<li id="'+key+'"><a href="#">'+value+'</a></li>'

        insert += '</ul>'

        insert += '</div>'

        sys.stdout.write(insert)

if __name__ == '__main__':
        sys.stdout.write("Content-Type: text/html")
        sys.stdout.write("\n")
        sys.stdout.write("\n")
        getAdmin()

