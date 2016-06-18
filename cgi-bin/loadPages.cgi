#!../venv/bin/python

import cgi,sys,os
import cgitb
cgitb.enable()

import json

import imp

loadUser = imp.load_source('loadUser','loadUser.cgi')

pagesDir = "../assignments/"

alist = "/alist"

def loadPages(course):
        try:
                with open(pagesDir+course+alist, 'r') as f:
                        return json.loads(f.read())

        except:
                return ""
        
def printPages():

        # here, we get the value for the course we want..

        form = cgi.FieldStorage()

        course = form.getvalue("classID")

        user,admin,grading = loadUser.getUser()

        grading = grading.split(",")

        admin = admin.split(",")
        full_priv = set(grading).union(set(admin))

        if course not in full_priv:
                sys.stdout.write('<script type="text/javascript">alert("Not authorized for that course!")</script>')
                quit()

        pageList = loadPages(course)

        if pageList == "":
                sys.stdout.write('<div id="pages"><p>Error: cannot locate assignments</p></div>')
                quit()

        if (len(pageList) == 0):
                sys.stdout.write('<div id="pages"><p>No assignments found</p></div>')
                quit()


        insert = '<div id="pages">'

        insert += '<p>Select an assignment: </p>'

        insert += "<ul>"

        for i in range(0, len(pageList)):
                insert += '<li id="'+pageList[i]["name"]+'"><a href="#">'+pageList[i]["name"]+"</a></li>"

        insert += "</ul>"
        
        insert += "</div>"

        sys.stdout.write(insert)

if __name__ == '__main__':
        sys.stdout.write("Content-Type: text/html")
        sys.stdout.write("\n")
        sys.stdout.write("\n")
        printPages()
