#!../venv/bin/python

import cgi,sys,os
import cgitb
cgitb.enable()

import json

import imp

import subprocess

loadUser = imp.load_source('loadUser','loadUser.cgi')
loadType = imp.load_source('loadType','loadType.cgi')
loadPDF = imp.load_source('loadPDF','loadPDF.cgi')

dirPath = "/g/" # or /comp/ for live version
tempInter = "/2016s" # remove for live version
gradingPath = "/grading/"

assignDir = "../assignments/"

cardName = "/scorecard"
alist = "/alist"

compOpen = '['
compClose = ']'

exOpen = '{'
exClose = '}'

headerChar = '*'
commentChar = '#'
compChar = '?'

saveButton = '<a href="#" id="save">Save</a>'

commentBoxStart = '<h3>Summary</h3><textarea name="comments" id="comments">'

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

                return '<p class="extra">'+comp+'<span class="input"><input type="number" name="excredit" max='+sval+' class="input" value="'+sprev+'"> max: '+sval+'</span></p>'

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
                # (2) It's locked, so it has a .lock suffix
                try:
                       with open(cardPath+lock, 'r') as f:
                                card = f.readlines()

                except:
                        # (3) There is no scorecard, so load the blank template instead
                        try:
                                with open(fullPath, 'r') as f:
                                        card = f.readlines()

                        # The other possibility is that there is no template to load, so push an error:
                        except:
                                sys.stdout.write('<div id="scorecard"><h1>Error: Unable to load scorecard</h1></div>')
                                quit()

        # convert card into usable HTML, each corresponding line of the template = a line of valid HTML
        card = map(str, map(parseCard, card))

        insert = '<div id="console">'

        # TODO: insert += '<div id="board">' # this is where we insert the code (and options on top)

        insert += '<div id="panel">'

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

        insert += '</div>'

        sys.stdout.write(insert)

def getScore(card, page):
        
        score = "0"
        ex = "0"
        curScore = "0"
        curEx = "0"
        s = card[int(page)-1]

        l = s.split(compOpen) # (1) get real (countable) score
        m = s.split(exOpen)   # (2) get extra credit score
        if (len(l) != 1):
                score = l[1].split(compClose)[0]
                sprev = l[1].split(scorePre)
                curScore = sprev[1].strip() if len(sprev) != 1 else str(float(score)/2)

        if (len(m) != 1):
                ex = m[1].split(exClose)[0]
                sprev = m[1].split(scorePre)
                if len(sprev) != 1: 
                        curEx = sprev[2].strip() if (len(sprev) > 2) else sprev[1].strip()

        return score, ex, curScore, curEx

def pdf(course, assignment, student, page, prev):

        fullPath = dirPath + course + tempInter + gradingPath + assignment + cardName

        cardPath = gradePath + student + "/" + course + "." + assignment

        # try to open the scorecard, there are three possibilities:
        # (1) It's unlocked, so has no suffix
        try:
                with open(cardPath, 'r') as f:
                        card = f.readlines()

        except:
                # (2) It's locked, so it has a .lock suffix
                try:
                        with open(cardPath+lock, 'r') as f:
                                card = f.readlines()

                except:
                        # (3) There is no scorecard, so load the blank template instead
                        try:
                                with open(fullPath, 'r') as f:
                                        card = f.readlines()

                        # The other possibility is that there is no template to load, so push an error:
                        except:
                                sys.stdout.write('<script type="text/javascript">Error: Unable to load scorecard</script>')
                                quit()

        # convert card into usable HTML, each corresponding line of the template = a line of valid HTML
        score, ex, curScore, curEx = getScore(card, page)

        svg, loadStudent = loadPDF.loadPDF(course, assignment, page, student, prev)

        if svg == "":
                sys.stdout.write('<div id="console"><script type="text/javascript">closePDF();alert("Unable to load next student, closing...");</script></div>')
                quit()

        insert = '<div id="console">'
        insert += '<div id="board">'+svg+'</div>'
        insert += '<div id="panel">'
        insert += '<div id="artOptions">'
        insert += '<input id="draw" type="button" onclick="draw()" value="draw">'
        insert += '&emsp;'
        insert += '<input id="text" type="button" onclick="text()" value="text">'
        insert += '&emsp;'
        insert += '<input id="drag" type="button" onclick="drag()" value="drag">'
        insert += '&emsp;'
        insert += '<input type="button" onclick="selectElements()" value="select">'
        insert += '<br>'

        insert += '<span id="drawColor">'
        insert += '<span id="drawWidth">Width: <input id="width" type="number" min="1" value="5" style="width:55px" oninput="radius=this.value/2;document.getElementById(\'cursor\').style.width=this.value+\'px\';document.getElementById(\'cursor\').style.height=this.value+\'px\'"></span>'
        insert += '<br>'
        insert += '<select onchange="document.getElementById(\'color\').value=document.getElementById(\'cursor\').style.background=brush=this.value" id="colorList">'
        insert += '<option value="#000000" selected>Black</option>'
        insert += '<option value="#0000ff">Blue</option>'
        insert += '<option value="#008000">Green</option>'
        insert += '<option value="#ff0000">Red</option>'
        insert += '<option value="#ffd700">Yellow</option>'
        insert += '<option value="#ffffff">White</option>'
        insert += '</select>'
        insert += '&emsp;'
        insert += '<input id="color" type="color" value="#000000" style="width:75px;height:32px;" onchange="document.getElementById(\'cursor\').style.background=brush=this.value;">'
        insert += '</span>'
        insert += '<span id="fontColor">'
        insert += '<span id="fontSize">Text size: <input id="fontsize" type="number" min="8" value="12" style="width:55px" oninput="setFontSize(this.value)"></span>'
        insert += '<br>'
        insert += '<select onchange="document.getElementById(\'fontColor\').value=fontColor=this.value" id="fontColorList">'
        insert += '<option value="#000000" selected>Black</option>'
        insert += '<option value="#0000ff">Blue</option>'
        insert += '<option value="#008000">Green</option>'
        insert += '<option value="#ff0000">Red</option>'
        insert += '<option value="#ffd700">Yellow</option>'
        insert += '<option value="#ffffff">White</option>'
        insert += '</select>'
        insert += '&emsp;'
        insert += '<input id="fontColorSel" type="color" value="#000000" style="width:75px;height:32px;" onchange="fontColor=this.value;">'
        insert += '</span>'
        insert += '</div>'
        insert += '<div id="changeOptions">'
        insert += '<input type="button" onclick="undo()" value="undo">'
        insert += '&emsp;'
        insert += '<input type="button" onclick="clean(\'all\')" value="clear all">'
        insert += '&emsp;'
        insert += '<input type="button" onclick="clean(\'text\')" value="clear text">'
        insert += '&emsp;'
        insert += '<input type="button" onclick="clean(\'lines\')" value="clear lines">'
        insert += '</div>'
        insert += '<div id="scoring">'
        insert += '<span id="courseNum">Course: <span id="courseValue" class="rightWrap">'+course+'</span></span>'
        insert += '<br>'
        insert += '<span id="assignNum">Assignment: <span id="assignValue" class="rightWrap">'+assignment+'</span></span>'
        insert += '<br>'
        insert += '<span id="pageNum">Page: <span id="pageValue" class="rightWrap">'+page+'</span></span>'
        insert += '<br>'
        insert += '<span id="studentName">UTLN: <span id="studentValue" class="rightWrap">'+loadStudent+'</span></span>'
        insert += '<br>'
        if score != "0":
                insert += '<label for="score">Score:</label>'
                insert += '<span class="rightWrap">'
                insert += '<input type="range" min="0" max="'+score+'" value="'+curScore+'" id="score" step="1">'
                insert += '&emsp;'
                insert += '<input type="number" value="'+curScore+'" min="0" max="'+score+'" id="score_value" style="width: 50px;">'
                insert += ' out of '+score+'&emsp;'
                insert += '<input type="button" onclick="maxScore()" value="max">'
                insert += '</span>'
                insert += '<br>'
        if ex != "0":
                insert += '<label for="exCredit">Extra credit:</label>' 
                insert += '<span class="rightWrap">'
                insert += '<input type="range" min="0" max="'+ex+'" value="'+curEx+'" id="exCredit" step="1">'
                insert += '&emsp;'
                insert += '<input type="number" value="'+curEx+'" min="0" max="'+ex+'" id="exCredit_value" style="width: 50px;">'
                insert += ' max: '+ex+'&emsp;'
                insert += '<input type="button" onclick="maxExtra()" value="max">'
                insert += '</span>'
        insert += '</div>'
        insert += '<div id="searchOptions">'
        insert += '<label for="studentSearch">Search for student by UTLN</label>'
        insert += '<span class="rightWrap"><input type="text" style="width: 75px;" id="studentSearch">&emsp;<input type="button" onclick="goSearch()" value="search"></span>'
        insert += '<br>'
        insert += '<label for="pageSearch">Go to page</label>'
        insert += '<span class="rightWrap"><input type="number" min="1" style="width: 50px;" id="pageSearch">&emsp;<input type="button" onclick="pageSearch()" value="go"></span>'
        insert += '<br>'
        insert += '</div>'
        insert += '<div id="saveOptions">'
        insert += '<input type="button" onclick="save()" value="save">'
        insert += '&emsp;'
        insert += '<br>'
        insert += '<input type="button" onclick="save(\'next\')" value="save and next">'
        insert += '&emsp;'
        insert += '<input type="button" onclick="save(\'close\')" value="save and exit">'
        insert += '<br>'
        insert += '<input type="button" onclick="skip(\'next\')" value="skip w/o saving">'
        insert += '&emsp;'
        insert += '<input type="button" onclick="skip(\'close\')" value="exit w/o saving">'
        insert += '</div>'
        insert += '</div>'

        insert += '<div id="cursor"></div>'

        insert += '<script type="text/javascript">genScoring();</script>'

        sys.stdout.write(insert)

def unknown():
        sys.stdout.write('<div id="scorecard"><h1>Unknown scoring format</h1></div>')
        quit()

def getCard():

        form = cgi.FieldStorage()

        course = form.getvalue("classID")
        assignment = form.getvalue("page")
        student = form.getvalue("student")
        page = form.getvalue("pageNum")
        prev = form.getvalue("prev")

        if student is None:
                student = ""   
        
        if prev is None:
                prev = ""

        user,admin,grading = loadUser.getUser()

        grading = grading.split(",")

        admin = admin.split(",")
        full_priv = set(grading).union(set(admin))

        if course not in full_priv:
                sys.stdout.write('<script type="text/javascript">alert("Not authorized for that course!");</script>')
                # insert logging of unauthorized entry here...
                quit()

        scoreType = loadType.getType(course, assignment)["type"]

        if scoreType == "scorecard":
                scorecard(course, assignment, student)
        elif scoreType == "pdf":
                pdf(course, assignment, student, page, prev)
        else:
                unknown()

        quit()

if __name__ == '__main__':
        sys.stdout.write("Content-Type: text/html")
        sys.stdout.write("\n")
        sys.stdout.write("\n")
        getCard()
