#!../venv/bin/python

import cgi,sys,os
import cgitb
cgitb.enable()

import json

import imp

import subprocess

loadUser = imp.load_source('loadUser','loadUser.cgi')
loadType = imp.load_source('loadType','loadType.cgi')

dirPath = "/g/" # or /comp/ for live version
tempInter = "/2016s" # remove for live version
gradingPath = "/grading/"

dirOnly = "/*/"

assignPath = "../assignments/"

inpExt = ".inprogress"
compExt = ".completed"

def getName(s):
        n = s.split("/")[-2].split(".")[0]
        return n

def getNames(course, assignment):

        fullPath = dirPath + course + tempInter + gradingPath + assignment + dirOnly

        # get all of the names
        # (1) start with the largest pool (all students)
        names = subprocess.Popen('ls -d -- ' + fullPath, shell=True, stdout=subprocess.PIPE).stdout.read().split()

        names = map(getName, names)

        names = set(names)

        if len(names) == 0:
                sys.stdout.write('<div id="error"><h1>No students found</h1></div>')
                quit()

        # then retrieve all completed students
        completedPath = assignPath + course + "/" + assignment + compExt
        try:
                with open(completedPath, 'r') as f:
                        com = sorted([line.rstrip() for line in f], key=str.lower)

        except:
                com = ""

        # and all students in progress
        inprogressPath = assignPath + course + "/" + assignment + inpExt
        try:
                with open(inprogressPath, 'r') as f:
                        inp = sorted([line.rstrip() for line in f], key=str.lower)

        except:
                inp = ""

        # (2) and take the inprogress/completed students out of the general pool
        names = sorted(list(names.difference(set(com), set(inp))), key=str.lower)

        return names, inp, com

def getCardSelection(course, assignment):
                
        names, inp, com = getNames(course, assignment)

        insert = '<div id="students">'

        insert += '<p class="title">List of students</li>'

        insert += "<ul>"

        for i in range(0, len(names)):
                insert += '<li id="'+names[i]+'"><a href="#">'+names[i]+'</a></li>'

        insert += "</ul>"

        insert += '</div>'

        insert += '<div id="inprogress">'

        insert += '<p class="title">In progress</li>'

        insert += '<ul>'

        for i in range(0, len(inp)):
                insert += '<li id="'+inp[i]+'"><a href="#">'+inp[i]+'</a></li>'

        insert += "</ul>"

        insert += "</div>"

        insert += '<div id="completed">'

        insert += '<p class="title">Completed</li>'

        insert += '<ul>'

        for i in range(0, len(com)):
                insert += '<li id="'+com[i]+'"><a href="#">'+com[i]+'</a></li>'

        insert += "</ul>"

        insert += "</div>"

        return insert

def getNamesByPage(course, assignment, page):

        fullPath = dirPath + course + tempInter + gradingPath + assignment + dirOnly

        # get all of the names
        # (1) start with the largest pool (all students)
        names = subprocess.Popen('ls -d -- ' + fullPath, shell=True, stdout=subprocess.PIPE).stdout.read().split()

        names = map(getName, names)

        names = set(names)

        numNames = len(names)

        if (numNames == 0):
                numNames = 1

        # then retrieve all completed students
        completedPath = assignPath + course + "/" + assignment + "." + str(page) + compExt
        try:
                with open(completedPath, 'r') as f:
                        com = [line.rstrip() for line in f]

        except:
                return numNames, 0
        
        return numNames, len(com)


def getPDFSelection(course, assignment, numPages):

        insert = '<div id="pdfpages">'

        insert += '<ul>'

        for i in range(0, numPages):
                names, com = getNamesByPage(course, assignment, i+1)
                numDone = (float(com)/names)*100
                numDoneStr = str(numDone)
                insert += '<li>'
                insert += '<span id="page'+str(i+1)+'"><a href="#">'+str(i+1)+'</a>&emsp;<progress value="'+numDoneStr+'" max="100"></progress>&emsp;'
                insert += '<label for="stuSearch'+str(i+1)+'">By UTLN:&emsp;</label><input type="text" id="stuSearch'+str(i+1)+'">&emsp;'
                insert += '<a href="#">Search</a></span>'
                insert += '</li>'
                #insert += '<br>'

        insert += '</ul>'
        insert += '</div>'

        return insert

def printNames():

        form = cgi.FieldStorage()

        course = form.getvalue("classID")
        assignment = form.getvalue("page")

        user,admin,grading = loadUser.getUser()

        grading = grading.split(",")

        admin = admin.split(",")
        full_priv = set(grading).union(set(admin))

        if course not in full_priv:
                sys.stdout.write('<script type="text/javascript">alert("Not authorized for that course!");</script>')
                # insert logging of unauthorized entry here...
                quit()

        assDetails = loadType.getType(course, assignment)

        scoreType = assDetails["type"]

        if (scoreType == "scorecard"):
                insert = getCardSelection(course, assignment)

        elif (scoreType == "pdf"):
                insert = getPDFSelection(course, assignment, int(assDetails["pages"]))

        sys.stdout.write(insert)

if __name__ == '__main__':
        sys.stdout.write("Content-Type: text/html")
        sys.stdout.write("\n")
        sys.stdout.write("\n")
        printNames()

