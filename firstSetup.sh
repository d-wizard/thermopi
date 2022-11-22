#!/bin/bash

# Make this directory accessable
chmod 755 .

# Make the Web Graph generator script accessable.
chmod 755 getTempChartArray.py

# Make Topic Log Path JSON accessable
chmod 644 TopicLogPath.json

# Make directory for log file
# mkdir -p /path/to/log/file/directory

# Make lock file for log
# touch /path/to/log/file.lock

# Make sure log files are accessable
# chmod 777 -R /path/to/base/log/directory

# Make sure web stuff is accessable
chmod 755 web
chmod 644 web/*

# Mount to webserver
# ln -nfs ${PWD}/web /path/to/webserver
