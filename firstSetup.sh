#!/bin/bash

# Make this directory accessable
chmod 755 .

# Make the Web Graph generator script accessable.
chmod 755 getTempChartArray.py

# Make Topic Log Path JSON accessable
chmod 644 TopicLogPath.json

# Make directory for log file
mkdir -p /mnt/4GBUSB/logs/mqtt/basement/storage
mkdir -p /mnt/4GBUSB/logs/mqtt/office
mkdir -p /mnt/4GBUSB/logs/mqtt/garage

# Make sure the log file and log file exist.
touch /mnt/4GBUSB/logs/mqtt/basement/storage/temperature.lock
touch /mnt/4GBUSB/logs/mqtt/basement/storage/temperature.log
touch /mnt/4GBUSB/logs/mqtt/office/temperature.lock
touch /mnt/4GBUSB/logs/mqtt/office/temperature.log
touch /mnt/4GBUSB/logs/mqtt/garage/temperature.lock
touch /mnt/4GBUSB/logs/mqtt/garage/temperature.log


# Make sure log files are accessable
chmod 777 $(find /mnt/4GBUSB/logs/mqtt -type d)
chmod 666 $(find /mnt/4GBUSB/logs/mqtt -type f)

# Make sure subscriptions are accessable
chmod 755 subscriptions
chmod 644 subscriptions/*

# Make sure web stuff is accessable
chmod 755 web
chmod 644 web/*

# Mount to webserver
# ln -nfs ${PWD}/web /path/to/webserver
