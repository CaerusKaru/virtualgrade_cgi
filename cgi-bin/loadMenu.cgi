#!../venv/bin/python

import cgi,sys,os
import cgitb
cgitb.enable()

import json

import imp

import subprocess

loadUser = imp.load_source('loadUser','loadUser.cgi')
loadPages = imp.load_source('loadPages','loadPages.cgi')

dirPath = "/g/" # or /comp/ for live version
tempInter = "/2016s" # remove for live version
gradingPath = "/grading/"

dirOnly = "/*/"

assignPath = "../assignments/"

inpExt = ".inprogress"
compExt = ".completed"

options = { "create":"Create/Import","delete":"Delete","publish":"Publish","export":"Export",
                "stats":"Statistics", "assign":"Assign Graders" }

noMenu = "Error: unknown menu"

def publish(course):
        
        pageList = loadPages.loadPages(course)
        if pageList == "":
                return "Error: unable to load assignments"

        # INVARIANT: We have now loaded a valid JSON-formatted list of assignments, which
        #            should contain a list of all of the publish/not-publish items
        insert = '<ul class="publish">'

        # TODO add "publish comments" toggle with separate id [Comments/No Comments]

        insert += '<li>Assignment</li>'

        insert += '<br><br>'

        for i in range(0, len(pageList)):
                insert += '<li id="'+pageList[i]["name"]+'">'+pageList[i]["name"]+'<label class="switch switch-slide"><input class="switch-input" type="checkbox" '
                if pageList[i]["publish"] == "y":
                        insert += "checked "

                insert += '/><span class="switch-label" data-on="Published" data-off="Not Published"></span> <span class="switch-handle"></span></label>'

                insert += '<label class="switch switch-slide"><input class="switch-input" id="com" type="checkbox" '

                if pageList[i]["publish_com"] == "y":
                        insert += "checked "

                insert += '/><span class="switch-label" data-on="Comments" data-off="No comments"></span> <span class="switch-handle"></span></label></li><br>'

        insert += '</ul>'

        return insert

def create(course):

        pageList = loadPages.loadPages(course)

        # TODO formatting: <
        #                   Assignment name: [_______]
        #                   Type: [drop-down: pdf/scorecard]
        #                  >

        # Below form is "how-to" on scorecard (pdf to come)
        # download link for template, and where scorecard must be stored


        insert = '<p>Assignment name: <span class="input_name"><input type="text" name="aname"></span></p>'

        insert += '<br>'

        insert += '<p>Select grading type:</p>'
        insert += '<div id="createForm">'
        insert += '<ul>'
        insert += '<li><a href="#">Scorecard</a></li>'
        insert += '<li><a href="#">PDF</a></li>'

        insert += '</ul>'
        insert += '</div>'

        insert += '<br>'

        insert += '<a id="create" href="#">Create</a>'

        return insert


def getAdmin():

        form = cgi.FieldStorage()

        course = form.getvalue("classID")
        menu = form.getvalue("menu")

        user,admin,grading = loadUser.getUser()

        admin = admin.split(",")

        if course not in admin:
                sys.stdout.write(course)
                sys.stdout.write('<script type="text/javascript">alert("Not authorized for that course!");</script>')
                # insert logging of unauthorized entry here...
                quit()

        insert = '<div id="menu">'

        if menu == "publish":
                insert += publish(course)
        elif menu == "create":
                insert += create(course)
#       elif menu == "delete":
#               insert += delete()
#       elif menu == "export":
#               insert += export()
#       elif menu == "assign":
#               insert += assign()
#       elif menu == "stats":
#               insert += menu()
        else:
                insert += noMenu

        insert += '</div>'

        sys.stdout.write(insert)

if __name__ == '__main__':
        sys.stdout.write("Content-Type: text/html")
        sys.stdout.write("\n")
        sys.stdout.write("\n")
        getAdmin()

