#!../venv/bin/python

import cgi,sys,os
import cgitb
cgitb.enable()

import json

import imp

loadUser = imp.load_source('loadUser','loadUser.cgi')

def printGrades():

        user,admin,grading = loadUser.getUser()

        grading = sorted(grading.split(","),key=str.lower)

        admin = sorted(admin.split(","), key=str.lower)
        full_priv = set(grading).union(set(admin))

        full_priv = sorted(list(full_priv), key=str.lower)

        insert = '<div id="content">'

        insert += '<p>Select a course: </p>'

        insert += "<ul>"

        for i in range(0, len(full_priv)):
                insert += '<li id="'+full_priv[i]+'"><a href="#">'+full_priv[i]+"</a></li>"

        insert += "</ul>"
        
        insert += "</div>"

        sys.stdout.write(insert)

if __name__ == '__main__':
        sys.stdout.write("Content-Type: text/html")
        sys.stdout.write("\n")
        sys.stdout.write("\n")
        printGrades()
