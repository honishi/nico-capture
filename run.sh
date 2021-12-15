#!/usr/bin/env bash

set -e

basedir=$(cd $(dirname $0);pwd)
program=${basedir}/nicocomment.py

logfile=${basedir}/log/nico-capture.log

cd ${basedir}

./main.py >> ${logfile}