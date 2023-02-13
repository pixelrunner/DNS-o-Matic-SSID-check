#!/usr/bin/env python3

import os
import os.path
import logging
import requests
import telegram
from time import strftime, sleep
from config.variables import Variables
import macwifi
import asyncio


Vars = Variables()

# mandatory vars
USERID = Vars.userId
PASSWORD = Vars.password
INTERVAL = Vars.interval
HOST = Vars.host
WILDCARD = Vars.wildcard
MX = Vars.mx
BACKUPMX = Vars.backupMx
IPADDR_SRC = Vars.ipAddressSrc

# optional vars
USETELEGRAM = Vars.useTelegram
CHATID = Vars.chatId
MYTOKEN = Vars.myToken
SITENAME = Vars.siteName
DEPENDWIRELESS = Vars.dependWireless
SSID = Vars.wirelessSSID
DEBUG = Vars.debug

# --- Globals ---
IPCACHE = "./config/ip.cache.txt"
VER = "0.2"
USER_AGENT = f"dnsomatic-update.py/{VER}"

# Setup logger
logger = logging.getLogger()
ch = logging.StreamHandler()
if DEBUG:
    logger.setLevel(logging.DEBUG)
    ch.setLevel(logging.DEBUG)
else:
    logger.setLevel(logging.INFO)
    ch.setLevel(logging.INFO)

formatter = logging.Formatter('[%(levelname)s] %(asctime)s %(message)s',
                              datefmt='[%d %b %Y %H:%M:%S %Z]')
ch.setFormatter(formatter)
logger.addHandler(ch)


def ip_changed(ip: str) -> bool:
    with open(IPCACHE, "r") as f:
        cached_ip = f.read()
        if cached_ip == ip:
            return False
        else:
            return True


def update_cache(ip: str) -> int:
    with open(IPCACHE, "w+") as f:
        f.write(ip)
    return 0


def send_notification(msg: str, chat_id: int, token: str) -> None:
    bot = telegram.Bot(token=token)
    bot.sendMessage(chat_id=chat_id, text=msg)
    logger.info('Telegram Group Message Sent')


def send_update(ip: str, user: str, passwd: str) -> None:
    update_url = f"https://updates.dnsomatic.com/nic/update?hostname={HOST}&myip={ip}&wildcard={WILDCARD}&mx={MX}&backmx={BACKUPMX}"
    logger.debug(f"request = '{update_url}'")
    headers = {'User-Agent': USER_AGENT}
    response = requests.get(update_url, headers=headers, auth=(user, passwd))
    logger.info(f"DNS-O-Matic Response: {response.text}")
    if USETELEGRAM:
        now = strftime("%B %d, %Y at %H:%M")
        notification_text = f"[{SITENAME}] WAN IP changed @ {now}. New IP == {ip}."  # noqa E501
        send_notification(notification_text, CHATID, MYTOKEN)


def wireless_check() -> bool:
    # check if dependant on SSID and then check SSID
    # this currently only works on Mac OSX
    try:
        if not DEPENDWIRELESS:
            return True
        elif SSID == macwifi.get_ssid():
            logger.debug(f"WiFi checked. SSID matches {SSID}")
            return True

        logger.info(f"WiFi checked. SSID does not match {SSID}. Skipping for {INTERVAL} seconds.")
        return False
    except Exception as e:
        logger.info(f"Error thrown when checking WiFi: {e}. Skipping for {INTERVAL} seconds.")
        return False


def main() -> None:
    while True:
        # check to see if wireless dependant and then check connected SSID against variable
        if wireless_check():
            # Grab current external IP
            current_ip = requests.get(IPADDR_SRC).text.rstrip('\n')

            # check to see if cache file exists and take action
            if os.path.exists(IPCACHE):
                if ip_changed(current_ip):
                    update_cache(current_ip)
                    logger.info(f"IP changed to {current_ip}")
                    send_update(current_ip, USERID, PASSWORD)
                else:
                    logger.info('No change in IP, no action taken')
            else:
                # No cache exists, create file
                update_cache(current_ip)
                logger.info(f"No cached IP, setting to {current_ip}")
                send_update(current_ip, USERID, PASSWORD)

        sleep(INTERVAL)


if __name__ == "__main__":
    main()