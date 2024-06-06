#!/bin/bash

# Script to start or stop the MoodleNet service.
# Capitalized variables should be changed according
# to you needs.

INSTALL_DIR=/home/ubuntu/moodlenet-dev
DEV_NAME=my-dev
LOG_PREFIX=/home/ubuntu/nohup.out

usage="Usage: $(basename $0) start|stop"

if [ -z $1 ]; then
  echo $usage
  exit 1
fi
if [ "$1 " == "stop " ]; then
  echo "Stop MoodleNet"
  killall node
  exit 0
fi
if [ "$1 " == "start " ]; then
  c=$(ps aux | grep node | grep start.mjs | wc -l)
  if [ $c -gt 1 ]; then
    echo "MoodleNet seems to be running"
    exit 1
  fi
  release_number=$(cat release.version)
  if [ $? -ne 0 ]; then
    echo "Warning: unknown release number"
    release_number=XX
  fi
  cd $INSTALL_DIR
  nohup npm run dev-start-backend $DEV_NAME > ${LOG_PREFIX}.${release_number} 2>&1 &
  sleep 2
  c=$(ps aux | grep node | grep start.mjs | wc -l)
  if [ $c -gt 1 ]; then
    echo "MoodleNet started"
    exit 0
  fi
  echo "MoodleNet could not be started"
  exit 1
fi 
echo $usage
exit 1