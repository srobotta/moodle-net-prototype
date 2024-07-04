#!/bin/bash

# Script to start or stop the MoodleNet service.
# Capitalized variables should be changed according
# to you needs.

INSTALL_DIR=/home/ubuntu/moodlenet-dev
DEV_NAME=my-dev
LOG_PREFIX=/home/ubuntu/nohup.out

usage="Usage: $(basename $0) start|stop"

function get_process_count() {
  return $(ps aux | grep node | grep start.mjs | wc -l)
}

function stop_mnet() {
  retry=0
  get_process_count
  if [ $? -gt 1 ]; then
    retry=3
  fi
  while [ $retry -gt 0 ]; do
    killall node
    sleep 1
    get_process_count
    if [ $? -lt 2 ]; then
      retry=0
    else
      retry=$((retry-1))
    fi
  done
  get_process_count
  if [ $? -gt 1 ]; then
    echo "Could not stop MoodleNet"
    exit 1
  fi
}

function start_mnet() {
  release_number=$(cat release.version)
  if [ $? -ne 0 ]; then
    echo "Warning: unknown release number"
    release_number=1
  fi
  cd $INSTALL_DIR
  nohup npm run dev-start-backend $DEV_NAME > ${LOG_PREFIX}.${release_number} 2>&1 &
  sleep 2
  get_process_count
  if [ $? -gt 1 ]; then
    echo "MoodleNet started"
    exit 0
  fi
  echo "MoodleNet could not be started"
  exit 1
}

if [ -z $1 ]; then
  echo $usage
  exit 1
fi
if [ "$1 " == "stop " ]; then
  echo "Stop MoodleNet"
  stop_mnet
  exit 0
fi
if [ "$1 " == "start " ]; then
  get_process_count
  if [ $? -gt 1 ]; then
    echo "MoodleNet seems to be running - restart"
    stop_mnet
  fi
  start_mnet
fi 

echo $usage
exit 1

