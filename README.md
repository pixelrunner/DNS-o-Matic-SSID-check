# DNS-o-Matic with Telegram and SSID check (for Mac)
A DNS-o-Matic updater for Mac that checks wireless SSID and then commits if SSIDs match. Also has the ability to send a telegram message. 

If you run on a non-Mac, then everything should work except the SSID check (so set to "0" or remove those references)

Features
========
- Telegram Integration
- SSID Check (only updates DNS-o-Matic if you are are on a defined SSID) 
- Runs every 300 seconds (by default)

Required extra modules
================
- python-telegram-bot (I used v20.1)
- macwifi (I used v0.0.5)


Steps to setup
==============

1) Rename the variables file to "variables.py".
2) update the variables file with your OpenDNS username and password
3) Optional: Update the OpenDNS/DNS-o-Matic variables (MX, BackupMX, wildcard, etc.). More details here: https://www.dnsomatic.com/docs/api
4) Optional: If you want to use Telegram then change the variable to "1", then update the variables. More details here: https://github.com/python-telegram-bot/python-telegram-bot/wiki/Introduction-to-the-API. I find the following good instructions for finding the chat ID: https://docs.influxdata.com/kapacitor/v1.6/event_handlers/telegram/
5) Optional: If you want to check your wireless SSID, then set the variable to "1" and update the SSID you want to use.

Testing
=======

When setting up DNS-o-Matic, you can test the update (outside of Python) by opening a browser and going to: https://updates.dnsomatic.com/nic/update?hostname=all.dnsomatic.com

If you are testing too frequently (~ less than a minute each time), then the DNS-o-Matic response might be negative as they do rate limit.