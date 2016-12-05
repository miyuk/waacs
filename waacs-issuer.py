#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os
from _conf_dict igParser import SafeConfigParser
import json
import logging
from logging.config import fileConfig
import qrcode
import requests
from tokenissuer import NfcIssuer, QrIssuer
from threading import Thread
import subprocess
import time
logger = logging.getLogger(__name__)


fileConfig(os.path.join(sys.path[0], "config/issuer_log.cfg"))
config = SafeConfigParser()
config.read(os.path.join(sys.path[0], "config/issuer.cfg"))
qr_conf_dict = dict(config.items("QrIssuer"))
qr_output_path = qr_conf_dict["qr_output_path"]
qr_update_interval = qr_conf_dict["qr_update_interval"]
wifi_conf_dict = dict(config.items("WifiInfo"))
ssid = wifi_conf_dict["ssid"]
api_conf_dict = dict(config.items("ApiClient"))
issuer_id = api_conf_dict["issuer_id"]
issuer_password = api_conf_dict["issuer_password"]
server_address = capi_conf_dict["server_address"]
server_port = api_conf_dict["server_port"]


def main(argv):
    nfc_issuer = NfcIssuer(ssid, api_conf_dict)
    nfc_issuer.start()
    qr_issuer = QrIssuer(ssid, api_conf_dict,
                         qr_output_path, qr_update_interval)
    qr_issuer.start()
    with open(os.devnull) as devnull:
        th = Thread(target=subprocess.call, args=(
            "startx".split(),), kwargs={"stdout": devnull})
        th.daemon = True
        th.start()
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            logger.warning("exit by KeyboardInterrupt")
            sys.exit(0)
        finally:
            nfc_issuer.stop()
            qr_issuer.stop()

if __name__ == '__main__':
    main(sys.argv)
