#!/bin/bash

chmod 755 .

touch changeSettings.log
chmod 666 changeSettings.log

chmod 755 changeSettings.py
chmod 755 ipc.py

chmod 755 getTempChartArray.py
touch temperature.lock
chmod 666 temperature.lock

touch web/tempCtrlSwitch.log
chmod 755 web
chmod 644 web/*