#!../venv/bin/python

import cgi,sys,os
import cgitb
cgitb.enable()

import json

import imp

import subprocess

loadUser = imp.load_source('loadUser','loadUser.cgi')

gradePath = "../grades/"

def getCourses(s):
        return s.split(".")[0]

def loadGrades():

        form = cgi.FieldStorage()

        user,admin,grading = loadUser.getUser()

        # TODO add logging of access here

        cardPath = gradePath + user + "/"

        cards = subprocess.Popen('ls ' + cardPath, shell=True, stdout=subprocess.PIPE).stdout.read().split()

        courses = set(map(getCourses, cards))

        courses = sorted(list(courses), key=str.lower)

        insert = '<div id="content">'

        insert += '<p>Select a course: </p>'

        insert += "<ul>"

        for i in range(0, len(courses)):
                insert += '<li id="'+courses[i]+'"><a href="#">'+courses[i]+"</a></li>"

        insert += "</ul>"
        
        insert += "</div>"

        sys.stdout.write(insert)

if __name__ == '__main__':
        sys.stdout.write("Content-Type: text/html")
        sys.stdout.write("\n")
        sys.stdout.write("\n")
        loadGrades()
