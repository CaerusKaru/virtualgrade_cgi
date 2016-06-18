#!../venv/bin/python

import cgi,sys,os
import cgitb
cgitb.enable()

import json

import imp

import subprocess

loadUser = imp.load_source('loadUser','loadUser.cgi')

compOpen = '['
compClose = ']'

exOpen = '{'
exClose = '}'

headerChar = '*'
commentChar = '#'
compChar = '?'

saveButton = '<a href="#" id="save">Save</a>'

commentBoxStart = '<h3>Summary</h3><textarea name="comments" id="comments" readonly>'

commentBoxEnd = '</textarea><br>'

gradePath = "../grades/"

lock = ".lock"

summary = ".summary"

scorePre = "--"

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

                return '<p class="comp">'+comp+'<span class="input"><input type="number" name="score" max='+sval+' class="input" value="'+sprev+'"> out of '+sval+'</span></p>'

        if (len(m) != 1):
                comp = m[0].strip()
                sval = m[1].split(exClose)[0]
                sprev = m[1].split(scorePre)
                sprev = "" if len(sprev) == 1 else sprev[1].strip()

                return '<p class="extra">'+comp+'<span class="input"><input type="number" name="excredit" max='+sval+' class="input" value="'+sprev+'"> out of '+sval+'</span></p>'

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

def getCard():

        form = cgi.FieldStorage()

        course = form.getvalue("classID")
        assignment = form.getvalue("page")

        user,admin,grading = loadUser.getUser()

        cardPath = gradePath + student + "/" + course + "." + assignment

        try:
                with open(cardPath, 'r') as f:
                        card = f.readlines()

        except:
                try:
                        with open(cardPath+lock, 'r') as f:
                                card = f.readlines()

                except:
                        try:
                                with open(fullPath, 'r') as f:
                                        card = f.readlines()

                        except:
                                sys.stdout.write('<div id="scorecard"><h1>Error: Unable to load scorecard</h1></div>')
                                quit()

        card = map(str, map(parseCard, card))

        insert = '<div id="scorecard">'

        for i in range(0, len(card)):
                insert += card[i]

        insert += commentBoxStart

        try:
                with open(cardPath + summary, 'r') as g:
                        insert += g.read()

        except:
                pass

        insert += commentBoxEnd

        insert += saveButton

        insert += '</div>'

        sys.stdout.write(insert)

if __name__ == '__main__':
        sys.stdout.write("Content-Type: text/html")
        sys.stdout.write("\n")
        sys.stdout.write("\n")
        getCard()
