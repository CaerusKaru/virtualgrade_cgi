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

scoreCard = ".score"

gradeDir = "../grades/"

def publish(course, assignment, pageType, numPages):
        
        if pageType == "scorecard":

                completedPath = pagesDir + course + "/" + assignment + compExt
                with open(completedPath, 'r') as f:
                        com = sorted([line.rstrip() for line in f], key=str.lower)

                for i in range(0, len(com)):
                        try:
                                newPath = gradeDir + com[i] + "/" + course + "." + assignment
                                os.rename(newPath + lock, newPath)
                        except:
                                pass

        elif pageType == "pdf":
                fullSet = set()
                for i in range(0, numPages):
                        completedPath = pagesDir + course + "/" + assignment + "." + str(i+1) + compExt
                        with open(completedPath, 'r') as f:
                                com = [line.rstrip() for line in f]

                        fullSet = set(com) if i == 0 else fullSet.intersection(set(com))

        
                fullList = list(fullSet)

                for i in range(0, len(fullList)):
                        try:
                                newPath = gradeDir + fullList[i] + "/" + course + "." + assignment
                                os.rename(newPath + lock, newPath)
                        except:
                                pass



def unpublish(course, assignment, pageType, numPages):

        if pageType == "scorecard":

                completedPath = pagesDir + course + "/" + assignment + compExt
                with open(completedPath, 'r') as f:
                        com = sorted([line.rstrip() for line in f], key=str.lower)
        
                for i in range(0, len(com)):
                        try:
                                newPath = gradeDir + com[i] + "/" + course + "." + assignment
                                os.rename(newPath, newPath + lock)
                        except:
                                pass
# we don't need lock, do we?
# we do, but which files do we lock, can we just have a .lock file? -- change to .unlock?
        elif pageType == "pdf":
                fullSet = set()
                for i in range(0, numPages):
                        completedPath = pagesDir + course + "/" + assignment + "." + str(i+1) + compExt
                        with open(completedPath, 'r') as f:
                                com = [line.rstrip() for line in f]

                        fullSet = set(com) if i == 0 else fullSet.intersection(set(com))

        
                fullList = list(fullSet)

                for i in range(0, len(fullList)):
                        try:
                                newPath = gradeDir + fullList[i] + "/" + course + "." + assignment
                                os.rename(newPath, newPath + lock)
                        except:
                                pass

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
                        pageList[i]["publish"] = pub
                        pageType = pageList[i]["type"]
                        numPages = pageList[i]["pages"] if pageType == "pdf" else "0"
                        break

        if pub == "y":
                publish(course, page, pageType, int(numPages))
        elif pub == "n":
                unpublish(course, page, pageType, int(numPages))

        with open(pagesDir + course + alist, 'w') as f:
                f.write(json.dumps(pageList))

if __name__ == '__main__':
        sys.stdout.write("Content-Type: text/html")
        sys.stdout.write("\n")
        sys.stdout.write("\n")
        changePublish()
