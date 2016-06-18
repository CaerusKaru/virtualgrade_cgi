#!../venv/bin/python

import cgi,sys,os
import cgitb
cgitb.enable()

import json

import imp

from subprocess import Popen,PIPE

loadUser = imp.load_source('loadUser','loadUser.cgi')
loadType = imp.load_source('loadType','loadType.cgi')
loadPages = imp.load_source('loadPages','loadPages.cgi')

dirPath = "/g/" # or /comp/ for live version
tempInter = "/2016s" # remove for live version
gradingPath = "/grading/"

pagesDir = "../assignments/"

cardName = "/scorecard"
alist = "/alist"

compOpen = '['
compClose = ']'

exOpen = '{'
exClose = '}'

headerChar = '*'
commentChar = '#'
compChar = '?'

commentBoxStart = '<h3>Summary</h3><textarea name="comments" id="comments" readonly>'

commentBoxEnd = '</textarea><br>'

gradePath = "../grades/"

lock = ".lock"

summary = ".summary"

scorePre = "--"

notAllowed = '<!DOCTYPE html5><html><head><meta charset="utf-8"></head><body><h1>Your instructor has opted to not release feedback for this assignment</h1></body></html>'

notFound = '<!DOCTYPE html5><html><head><meta charset="utf-8"></head><body><h1>Error: Unable to load scorecard</h1></body></html>'

unknownFormat = '<!DOCTYPE html5><html><head><meta charset="utf-8"></head><body><h1>Unknown scoring format</h1></body></html>'

def header(s):
        return '<h2 class="header">'+s+'</h2>'

def component(s):
        l = s.split(compOpen)
        m = s.split(exOpen)
        if (len(l) != 1):
                comp = l[0].strip()
                sval = l[1].split(compClose)[0]
                sprev = l[1].split(scorePre)
                sprev = "" if len(sprev) == 1 else sprev[1].strip()

                return '<p class="comp">'+comp+'<span class="input"><input type="number" name="score" max='+sval+' class="input" value="'+sprev+'" readonly> out of '+sval+'</span></p>'

        if (len(m) != 1):
                comp = m[0].strip()
                sval = m[1].split(exClose)[0]
                sprev = m[1].split(scorePre)
                sprev = "" if len(sprev) == 1 else sprev[1].strip()

                return '<p class="extra">'+comp+'<span class="input"><input type="number" name="excredit" max='+sval+' class="input" value="'+sprev+'" readonly> max: '+sval+'</span></p>'

def comment(s):
        return '<p class="comment">'+s+'</p>'

def parseCard(s):
        if (s[0] == headerChar):
                return header(s[1:].lstrip())
        elif (s[0] == compChar):
                return component(s[1:].lstrip())
        elif (s[0] == commentChar):
                return comment(s[1:].lstrip())
        else:
                return ' '                

def scorecard(course, assignment, student):

        fullPath = dirPath + course + tempInter + gradingPath + assignment + cardName

        cardPath = gradePath + student + "/" + course + "." + assignment

        # try to open the scorecard, there are three possibilities:
        # (1) It's unlocked, so has no suffix
        try:
                with open(cardPath, 'r') as f:
                        card = f.readlines()

        except:
                sys.stdout.write(notFound)
                quit()

        # convert card into usable HTML, each corresponding line of the template = a line of valid HTML
        card = map(str, map(parseCard, card))

        insert = '<!DOCTYPE html5>'

        insert += '<html><head><meta charset="utf-8"><link href="data/main.css" rel="stylesheet" />'
        insert += '<title>Comments for '+assignment+'</title>'
        insert += '</head><body>'

        insert += '<div id="roc">'

        for i in range(0, len(card)):
                insert += card[i]

        insert += commentBoxStart

        try:
                with open(cardPath + summary, 'r') as g:
                        insert += g.read()

        except:
                pass

        insert += commentBoxEnd

        insert += '</div></body></html>'

        sys.stdout.write("Content-Type: text/html")
        sys.stdout.write("\n")
        sys.stdout.write("\n")
        sys.stdout.write(insert)

def pdf(course, assignment, student):

        cardPath = gradePath + student + "/" + course + "." + assignment + ".*.svg"

        convertCmd = ['/usr/sup/bin/convert', '-density', '150', "-adjoin", cardPath, '-quality', '100', '-sharpen', '0x1.0', 'pdf:-']

        process = Popen(convertCmd, stdin=PIPE,stdout=PIPE,stderr=PIPE)

        outputPDF,err = process.communicate()

        sys.stdout.write("Content-Type: application/pdf\n")
        sys.stdout.write("Content-Disposition: attachment; filename=COMP"+course+"_"+assignment+".pdf\n")
        sys.stdout.write("\n")
        sys.stdout.write(outputPDF)


def unknown():
        sys.stdout.write(unknownFormat)
        quit()

def getCard():

        form = cgi.FieldStorage()

        course = form.getvalue("classID")
        assignment = form.getvalue("page")

        user,admin,grading = loadUser.getUser()

        pageList = loadType.getType(course, assignment)

        if pageList['publish_com'] == "n":
                sys.stdout.write("Content-Type: text/html")
                sys.stdout.write("\n")
                sys.stdout.write("\n")
                sys.stdout.write(notAllowed)
                quit()

        scoreType = pageList["type"]

        if scoreType == "scorecard":
                scorecard(course, assignment, user)
        elif scoreType == "pdf":
                pdf(course, assignment, user)
        else:
                unknown()

        quit()

if __name__ == '__main__':
        getCard()
