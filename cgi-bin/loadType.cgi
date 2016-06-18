#!../venv/bin/python

import cgi,sys,os
import cgitb
cgitb.enable()

import json

pagesDir = "../assignments/"
alist = "/alist"

def getType(course, assignment):

        try:
                with open(pagesDir+course+alist, 'r') as f:
                        pageList = json.loads(f.read())        

        except:
                sys.stdout.write('<script type="text/javascript">alert("Error loading assignment type");</script>')
                quit()

        for i in range(0, len(pageList)):
                if pageList[i]["name"] == assignment:
                        return pageList[i]

if __name__ == '__main__':
        sys.stdout.write("Content-Type: text/html")
        sys.stdout.write("\n")
        sys.stdout.write("\n")
        sys.stdout.write(getType())
