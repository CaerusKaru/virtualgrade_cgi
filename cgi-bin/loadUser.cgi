#!../venv/bin/python

import cgi,sys,os
import cgitb

cgitb.enable()

import json
import subprocess

from parse import *

def getUser():
        remoteUser = os.environ['REMOTE_USER']
        groups = subprocess.Popen('./gfind.sh '+remoteUser, shell=True, stdout=subprocess.PIPE).stdout.read().strip()
        
        groups += "," # added to allow indexing to end

        admin = ','.join(r.fixed[0] for r in findall("ta{},", groups))
        grading = ','.join(r.fixed[0] for r in findall("grade{},", groups))

        return (remoteUser,admin,grading)

if __name__ == '__main__':
        remoteUser,admin,grading = getUser()
        
        sys.stdout.write("Content-Type: application/json")
        sys.stdout.write("\n")
        sys.stdout.write("\n")
        print json.dumps({'user':remoteUser,'admin':admin,'grading':grading})
