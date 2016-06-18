#!../venv/bin/python

import cgi,sys,os
import cgitb
cgitb.enable()

import json
import imp
from subprocess import Popen,PIPE,call,check_output
import random

loadUser = imp.load_source('loadUser','loadUser.cgi')

dirPath = "/g/" # or /comp/ for live version
tempInter = "/2016s" # remove for live version
gradingPath = "/grading/"

dirOnly = "/*/"

gradePath = "../grades/"

assignPath = "../assignments/"

inpExt = ".inprogress"
compExt = ".completed"

def getName(s):
        n = s.split("/")[-2].split(".")[0]
        return n

def getRandomStudent(course, assignment, page, prev):
        fullPath = dirPath + course + tempInter + gradingPath + assignment + dirOnly

        # get all of the names
        # (1) start with the largest pool (all students)
        names, error = Popen(['bash','-c','ls -d -- ' + fullPath], stdin=PIPE, stdout=PIPE, stderr=PIPE).communicate()
        names = names.split()
        names = [line.strip() for line in names]

        names = map(getName, names)

        names = set(names)

        if len(names) == 0:
                return ""

        # then retrieve all completed students
        completedPath = assignPath + course + "/" + assignment + "." + page + compExt
        try:
                with open(completedPath, 'r') as f:
                        com = sorted([line.rstrip() for line in f], key=str.lower)

        except:
                com = []

        fresh = names.difference(set(com))
        fresh = fresh.difference(set(prev.split()))

        if len(list(fresh)) == 0:
                return ""

        return random.choice(list(fresh))

def getNums(s):
        n = s.split("/")[-1].split(".")[-1]
        return int(n)

def getFromSource(course, assignment, page, student):

        origin,error = Popen(['bash','-c','pwd'], stdin=PIPE, stdout=PIPE, stderr=PIPE).communicate()
        origin = origin.strip()

        fullPath = dirPath + course + tempInter + gradingPath + assignment + "/" + student
        names, error = Popen(['bash','-c','ls -d -- ' + fullPath + "*"], stdin=PIPE, stdout=PIPE, stderr=PIPE).communicate()
        names = names.split()
        names = [line.strip() for line in names]

        nums = map(getNums, names)

        mostRecent = str(max(nums))

        fullPath += "." + mostRecent + "/" + "p" + page + ".pdf"

#        svgPath = origin + "/" + gradePath + student + "/" + course + "." + assignment + "." + page + ".svg"

        convertCmd = ['/usr/sup/bin/convert', '-verbose', '-density', '150', fullPath, '-quality', '100', '-sharpen', '0x1.0', 'svg:-'] 

        command, error = Popen(convertCmd, stdin=PIPE,stdout=PIPE,stderr=PIPE).communicate()

        # the only time we write the svg to file is when we save it
        # this allows for automatic updating if there's a newer version available
        # after a grader 'views' but does not 'grade'
        # an edge case definitely, but we don't want to commit to a version before we have to

        if 'svg' in command:
                return command
        else:
                return '<script type="text/javascript">alert("Unable to find student!");</script>'

# if we ever want to write to the file immediately in the future:
#        try:
#                with open(svgPath, "r") as f:
#                        return f.read()
#        except:
#                return '<script type="text/javascript">alert("Unable to find student!");</script>'

def loadPDF(course, assignment, page, student, prev):

        random = (student == '')

        # get the permissions for the current 'grader'
        user,admin,grading = loadUser.getUser()

        grading = grading.split(",")

        admin = admin.split(",")
        full_priv = set(grading).union(set(admin))

        # only save the card if the grader has permission to do so
        if course not in full_priv:
                sys.stdout.write('<script type="text/javascript">alert("Not authorized for that course!");</script>')
                # TODO: insert logging of unauthorized entry here...
                quit()

        if random:
                student = getRandomStudent(course, assignment, page, prev)

        if student == "":
                return "",""

        svgPath = gradePath + student + "/" + course + "." + assignment + "." + page + ".svg" 

        try:
                with open(svgPath, "r") as f:
                        svg_load = f.read()
        except:
                svg_load = getFromSource(course, assignment, page, student)
        
        return svg_load, student

if __name__ == '__main__':
        
        sys.stdout.write("Content-Type: text/html")
        sys.stdout.write("\n")
        sys.stdout.write("\n")
