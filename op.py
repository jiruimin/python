#!/usr/bin/python3

import os

def git_pull():
    result = os.popen('git add . && git commit -m "jirm" && git push origin master')
    print (result.read())

git_pull()