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

cardName = "/scorecard"

gradePath = "../grades/"

scorePre = "--"

scoreDiv = "/"

compOpen = "["
exOpen = "{"

score = ".score"

lock = ".lock"

grader = ".gradedby"

cardDir = "../assignments/"

com_card = ".completed"

# createCard -- creates the card included the score formatting (--n, n=score)
def updateCard(template, scoreList, page, new):
                
        line = template[page]
        score = scoreList[0]
        ex = scoreList[1]

        scorePresent = compOpen in line
        exPresent = exOpen in line
        
        if new:
                template[page] = template[page].strip()
                if scorePresent:
                        template[page] += scorePre + score 
                if exPresent:
                        template[page] += scorePre + ex
                template[page] += "\n"

        else:
                rawScore = line.split(scorePre)[0].strip()
                template[page] = rawScore
                if scorePresent:
                        template[page] += scorePre + score 
                if exPresent:
                        template[page] += scorePre + ex
                template[page] += "\n"

        return template

def savePDF():

        # get all of the necessary parameters from the POST field
        form = cgi.FieldStorage()
        course = form.getvalue("classID")
        assignment = form.getvalue("page")
        page = form.getvalue("pageNum")
        svg = form.getvalue("svg")
        scjson = form.getvalue("sc")
        scorecard = json.loads(scjson)
        student = form.getvalue("student")

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

        svgPath = gradePath + student + "/" + course + "." + assignment + "." + page + ".svg"

        try:
                with open(svgPath, "w") as f:
                        f.write(svg)
        except:
                # TODO: print error statement to log here
                pass


        # INVARIANT: the grader has full permissions to grade, so start manipulating
        #            the files
        fullPath = dirPath + course + tempInter + gradingPath + assignment + cardName

        # open the scorecard template
        # if it doesn't exist, there is no real assignment to grade
        try:
                with open(fullPath, 'r') as f:
                        card = f.readlines()

        except:
                quit()

        # INVARIANT: We have a valid grade grading a valid assignment
        # Note: the only thing we can't check without explicit course rosters is
        #       whether or not the student is a real student in the course, but 
        #       this is worth conceding to avoid the extra hassle

        # this path represents an unlocked scorecard
        cardPath = gradePath + student + "/" + course + "." + assignment

        # Create the grading directory for our student, if it already exists,
        # just continue with no issue
        try:
                os.mkdir(gradePath + student, 0700)

        except:
                pass

        pageList = loadPages.loadPages(course)
        for i in range(0, len(pageList)):
                if pageList[i]["name"] == assignment:
                        pub = (pageList[i]["publish"] == "y")

        # if the unlocked scorecard exists, write to it
        if os.path.isfile(cardPath):
                with open(cardPath, 'r') as f:
                        oldCard = f.readlines()
                newCard = updateCard(oldCard, scorecard, int(page)-1, False)
                with open(cardPath, 'w') as f:
                        f.writelines(newCard)

        # if it's locked, write to that card instead
        elif os.path.isfile(cardPath + lock):
                
                with open(cardPath + lock, 'r') as f:
                        oldCard = f.readlines()
                newCard = updateCard(oldCard, scorecard, int(page)-1, False)
                with open(cardPath + lock, 'w') as f:
                        f.writelines(newCard)

                if pub:
                        os.rename(cardPath + lock, cardPath)

        # otherwise, create the locked version of the card based on the
        # template read in earlier
        else:
                newCard = updateCard(card, scorecard, int(page)-1, True)
                
                if pub:
                        with open(cardPath, 'a') as f:
                                f.writelines(newCard)

                else:
                        with open(cardPath + lock, 'a') as f:
                                f.writelines(newCard)

        with open(cardPath + grader, 'w') as f:
                f.write(user)

        assignPath = cardDir + course + "/" + assignment + "." + page + com_card

        with open(assignPath, 'r+') as f:
                com_list = [line.rstrip() for line in f]
                if student not in com_list:
                        com_list += [student]
                        f.seek(0)
                        f.write('\n'.join(com_list)+'\n')
                        f.truncate()

if __name__ == '__main__':
        
        sys.stdout.write("Content-Type: text/html")
        sys.stdout.write("\n")
        sys.stdout.write("\n")
        savePDF()
