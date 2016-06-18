#!../venv/bin/python

import cgi,sys,os
import cgitb
cgitb.enable()

import json

import imp

loadUser = imp.load_source('loadUser','loadUser.cgi')

def printGrades():

        user,admin,grading = loadUser.getUser()

        admin = sorted(admin.split(","),key=str.lower)      

        insert = '<div id="content"><p>Select a course: '

        insert += "<ul>"

        for i in range(0, len(admin)):
                insert += '<li id="'+admin[i]+'"><a href="#">'+admin[i]+'</a></li>'

        insert += "</ul></p></div>"

        sys.stdout.write(insert)

if __name__ == '__main__':
        sys.stdout.write("Content-Type: text/html")
        sys.stdout.write("\n")
        sys.stdout.write("\n")
        printGrades()
