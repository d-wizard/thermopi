#!/bin/bash

# Make this directory accessable
chmod 755 .

# Make the Web Graph generator script accessable.
chmod 755 getTempChartArray.py

# Make Topic Log Path JSON accessable
chmod 644 TopicLogPath.json

# Make directory for log file
# Make sure lock file / log file exist.

# Make sure the log file and log file exist.
# touch /path/to/log/file.lock
# touch /path/to/log/file.log

# Make sure log files are accessable
chmod 777 $(find /path/to/base/log/directory -type d)
chmod 666 $(find /path/to/base/log/directory -type f)

# Make sure subscriptions are accessable
chmod 755 subscriptions
chmod 644 subscriptions/*

# Make sure web stuff is accessable
chmod 755 web
chmod 644 web/*

# Mount to webserver
# ln -nfs ${PWD}/web /path/to/webserver
