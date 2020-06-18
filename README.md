# thermopi

This project uses the following:
1) Raspberry Pi (any one should do)
2) Sunkee DS18B20 Temperature Sensor
3) TP Link HS1xx Smart Power Switch
4) A webserver running on the Raspberry Pi that supports PHP
---
Initialize the Repo:
* /path/to/thermopi/firstSetup.sh
---
Create symbolic link of the web folder to the webserver:
* sudo ln -nfs /path/to/thermopi/web /path/to/webserver/thermopi
---
Create Cron Job to run the temperatureControlSwitch.py script
* Run:
    * crontab -e
* Add these lines to the end to run at start up
    * @reboot python /path/to/thermopi/temperatureControlSwitch.py