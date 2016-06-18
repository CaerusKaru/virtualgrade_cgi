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

compChar = "?"

scoreDiv = "/"

compOpen = "["
compClose = "]"

score = ".score"

lock = ".lock"

summary = ".summary"
grader = ".gradedby"

cardDir = "../assignments/"

inp_card = ".inprogress"
com_card = ".completed"

# lineScore -- parse a given line to find the score (if not extra credit)
def lineScore(line):
        
        # split based on component open
        l = line.split(compOpen)
        # if the line is graded (not ex. credit), return the score value
        if (len(l) != 1):
                return float(l[1].split(compClose)[0])

        # otherwise, it's an extra credit line, which does not contribute
        # to total score
        else:
                return 0

# updateCard -- updates an existing card which already has formatting and scoring
def updateCard(oldCard, scoreList):

        scoreIndex, totalScore, maxScore = 0,0,0
        for i in range(0, len(oldCard)):
                line = oldCard[i]
                if line[0] == compChar:
                        lineDec = line.split(scorePre)
                        lineDec[-1] = scoreList['scores'][scoreIndex] + '\n'
                        maxScore += lineScore(line)
                        totalScore += float(scoreList['scores'][scoreIndex])
                        scoreIndex += 1
                        oldCard[i] = scorePre.join(lineDec)

        return oldCard, totalScore, maxScore

# createCard -- creates the card included the score formatting (--n, n=score)
def createCard(template, scoreList):
                
        scoreIndex, totalScore, maxScore = 0,0,0
        for i in range(0, len(template)):
                line = template[i]
                if line[0] == compChar:
                        template[i] = template[i][:-1] + scorePre + scoreList['scores'][scoreIndex] + "\n"
                        maxScore += lineScore(line)
                        totalScore += float(scoreList['scores'][scoreIndex])
                        scoreIndex += 1

        return template, totalScore, maxScore

def saveCard():

        # get all of the necessary parameters from the POST field
        form = cgi.FieldStorage()
        course = form.getvalue("classID")
        assignment = form.getvalue("page")
        scjson = form.getvalue("scorecard")
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
                newCard, totalScore, maxScore = updateCard(oldCard, scorecard)
                with open(cardPath, 'w') as f:
                        f.writelines(newCard)

        # if it's locked, write to that card instead
        elif os.path.isfile(cardPath + lock):
                
                with open(cardPath + lock, 'r') as f:
                        oldCard = f.readlines()
                newCard, totalScore, maxScore = updateCard(oldCard, scorecard)
                with open(cardPath + lock, 'w') as f:
                        f.writelines(newCard)

                if pub:
                        os.rename(cardPath + lock, cardPath)

        # otherwise, create the locked version of the card based on the
        # template read in earlier
        else:
                newCard, totalScore, maxScore = createCard(card, scorecard)
                
                if pub:
                        with open(cardPath, 'a') as f:
                                f.writelines(newCard)

                else:
                        with open(cardPath + lock, 'a') as f:
                                f.writelines(newCard)

        # INVARIANT: We now have the total score earned by the student
        #            as a single floating-point number

        # overwrite any of the previous summary with the new summary
        # since it's just text
        with open(cardPath + summary, 'w') as f:
                f.write(scorecard['summary'])

        # same with the grader, only count the last person to grade
        # possibility for abuse, but should be reconsidered later
        with open(cardPath + grader, 'w') as f:
                f.write(user)

        assignPath = cardDir + course + "/" + assignment

        # if there are some blank areas in scorecard, it's still in progress
        if '' in scorecard['scores']:
                # open with r+ to allow for updating (need to reseek to write)
                with open(assignPath + inp_card, 'r+') as f:
                        inp_list = [line.rstrip() for line in f]
                        # only add the student to the inp list if not already there          
                        if student not in inp_list:
                                inp_list += [student]
                                f.seek(0)
                                f.write('\n'.join(inp_list)+'\n')
                                f.truncate()
        
        # if there are no blank areas, it's complete, but might've been in progress
        # so we have to remove it from that list if it's there
        else:
                with open(assignPath + inp_card, 'r+') as f:
                        inp_list = [line.rstrip() for line in f]
                        try:
                                inp_list.remove(student)
                        except:
                                pass
                        f.seek(0)
                        f.write('\n'.join(inp_list)+'\n')
                        f.truncate()

                with open(assignPath + com_card, 'r+') as f:
                        com_list = [line.rstrip() for line in f]
                        if student not in com_list:
                                com_list += [student]
                                f.seek(0)
                                f.write('\n'.join(com_list)+'\n')
                                f.truncate()

        # now write the total score file as two floating point numbers, the total
        # score and the max score

        with open(cardPath + score, 'w') as f:
                f.write(str(totalScore) + scoreDiv + str(maxScore))

if __name__ == '__main__':
        
        sys.stdout.write("Content-Type: text/html")
        sys.stdout.write("\n")
        sys.stdout.write("\n")
        saveCard()
