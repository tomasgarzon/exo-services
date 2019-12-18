#!/bin/bash

MY_PATH="`dirname \"$0\"`"              # relative
MY_PATH="`( cd \"$MY_PATH\" && cd .. && pwd )`"  # absolutized and normalized
if [ -z "$MY_PATH" ] ; then
  # error; for some reason, the path is not accessible
  # to the script (e.g. permissions re-evaled after suid)
  exit 1  # fail
fi

echo "Working path: $MY_PATH"

CONFIG=$MY_PATH/scripts/flake8.cfg
echo "Using config: $CONFIG"

if [ "$1" != "" ]; then
    flake8 --config=$CONFIG $MY_PATH/$1 | $MY_PATH/scripts/flake8_colorizer.py
else
    flake8 --config=$CONFIG $MY_PATH | $MY_PATH/scripts/flake8_colorizer.py
fi
