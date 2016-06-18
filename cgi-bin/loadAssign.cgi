#!../venv/bin/python

import cgi,sys,os
import cgitb
cgitb.enable()

import json

import imp

import subprocess

loadUser = imp.load_source('loadUser','loadUser.cgi')
loadType = imp.load_source('loadType','loadType.cgi')

pagesDir = "../grades/"

lock = ".lock"
summary = ".summary"
score = ".score"
gradedby = ".gradedby"

noSuffix = "*.*.*"

scoreDiv = "/"

scorePre = "--"

compOpen = "["
exOpen = "{"

def isCourse(line, course):
        return line.split(".")[0] == course

def getAssign(s):
        return s.split(".")[1]

def getPDFScore(rawScore):

        # rawScore is an array representing the lines with the newlines removed

        totalScore,maxScore = 0,0

        for i in range(0, len(rawScore)):
                line = rawScore[i]
                parseLine = line.split(scorePre)
                hasScore = compOpen in parseLine[0]
                hasEx = exOpen in parseLine[0]
                if hasScore:
                        score = parseLine[1]
                        totalScore += float(score)
                        maxScore += float(score)
                if hasEx:
                        ex = parseLine[2] if hasScore else parseLine[1]
                        totalScore += float(ex)

        return str(totalScore),str(maxScore)

def printPages():

        # here, we get the value for the course we want..

        form = cgi.FieldStorage()

        course = form.getvalue("classID")

        user,admin,grading = loadUser.getUser()

        gradePath = pagesDir + user

        assignments = subprocess.Popen('ls ' + gradePath + ' -I "'+noSuffix+'"', shell=True, stdout=subprocess.PIPE).stdout.read().split() 

        # Here is where we load all of the available unlocked assignments

        assignments = [x for x in assignments if isCourse(x, course)]

        assignments_map = map(getAssign, assignments)

        if (len(assignments) == 0):
                sys.stdout.write('<div id="grades"><p>No assignments found</p></div>')
                quit()

        insert = '<div id="grades">'

        # Credit to C. Gregg for using a hidden form in legacy VG
        insert += '<form style="display: hidden;" action="cgi-bin/loadROC.cgi" method="POST" id="downloadPDF">'
        insert += '<input type="hidden" id="courseDownload" name="classID" value="" />'
        insert += '<input type="hidden" id="pageDownload" name="page" value="" />'
        insert += '</form>'

        insert += "<table>"

        insert += '<thead><tr>'

        insert += '<th>Assignment</th>'
        insert += '<th>Grade</th>'
        insert += '<th>Out of</th>'
        insert += '<th>Percent</th>'
        insert += '<th>Comments</th>'
        insert += '<th>Graded by</th>'

        insert += '</tr></thead>'

        insert += '<tbody>'

        for i in range(0, len(assignments)):

                pageList = loadType.getType(course, assignments_map[i])
                scoreType = pageList["type"]

                if scoreType == "scorecard":
                        scorePath = gradePath + "/" + assignments[i] + score
                elif scoreType == "pdf":
                        scorePath = gradePath + "/" + assignments[i]
                with open(scorePath, 'r') as f:
                        rawScore = [line.strip() for line in f.readlines()]
        
                with open(gradePath + "/" + assignments[i] + gradedby, 'r') as f:
                        grader = f.read()
        

                totalScore = "0"
                maxScore = "1"

                if scoreType == "scorecard":
                        totalScore = rawScore[0].split(scoreDiv)[0]
                        maxScore = rawScore[0].split(scoreDiv)[1]

                elif scoreType == "pdf":
                        totalScore, maxScore = getPDFScore(rawScore)

                insert += '<tr>'
                insert += '<td>'+assignments_map[i]+'</td>'
                insert += '<td>'+totalScore+'</td>'
                insert += '<td>'+maxScore+'</td>'
                if maxScore == 0:
                        maxScore = 1
                insert += '<td>'+format((float(totalScore)/float(maxScore))*100, '.2f')+'</td>'
                if pageList["publish_com"] == "y":
                        if scoreType == "scorecard":
                                insert += '<td>'+'<a href="#">scorecard</a>'+'</td>'
                        elif scoreType == "pdf":
                                insert += '<td>'+'<a href="#">pdf</a>'+'</td>'
                else:
                        insert += '<td>none</td>'
        
                insert += '<td>'+grader+'</td>'
                insert += '</tr>'

        insert += '</tbody>'

        insert += "</table>"
        
        insert += "</div>"

        sys.stdout.write(insert)

if __name__ == '__main__':
        sys.stdout.write("Content-Type: text/html")
        sys.stdout.write("\n")
        sys.stdout.write("\n")
        printPages()
