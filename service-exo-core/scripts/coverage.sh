#!/bin/bash

MY_PATH="`dirname \"$0\"`"              # relative
MY_PATH="`( cd \"$MY_PATH\" && cd .. && pwd )`"  # absolutized and normalized
if [ -z "$MY_PATH" ] ; then
  # error; for some reason, the path is not accessible
  # to the script (e.g. permissions re-evaled after suid)
  exit 1  # fail
fi

echo "Working path: $MY_PATH"

coverage run --omit=*__init__*,*migrations* --include=social/*,address/*,company/*,contact/*,files/*,mails/*,meetings/*,news/*,people/*,project/*,widgets/*,videocall/*,utils/* $MY_PATH/manage.py test
coverage html -d $MY_PATH/htmlcov

if [ "$(expr substr $(uname -s) 1 5)" == "Linux" ]; then
    xdg-open $MY_PATH/htmlcov/index.html
else
    open $MY_PATH/htmlcov/index.html
fi
