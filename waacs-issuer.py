﻿#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os
from ConfigParser import SafeConfigParser
import json
import logging
from logging.config import fileConfig
fileConfig(os.path.join(sys.path[0], "config/issuer_log.cfg"))
logger = logging.getLogger(__name__)
import qrcode
import requests
from tokenissuer import NfcIssuer, QrIssuer
from threading import Thread
import subprocess
import time
config = SafeConfigParser()
config.read(os.path.join(sys.path[0], "config/issuer.cfg"))
qr_output_path = config.get("QrIssuer", "qr_output_path")
qr_update_interval = config.getint("QrIssuer", "qr_update_interval")
ssid = config.get("WifiInfo", "ssid")
issuer_id = config.get("ApiClient", "issuer_id")
issuer_password = config.get("ApiClient", "issuer_password")
server_address = config.get("ApiClient", "server_address")
server_port = config.getint("ApiClient", "server_port")


def main(argv):
    # nfc_issuer = NfcIssuer(server_address, server_port, issuer_id, issuer_password)
    # nfc_issuer.start()
    qr_issuer = QrIssuer(ssid, server_address, server_port, issuer_id, issuer_password,
                         qr_output_path, qr_update_interval)
    qr_issuer.start()
    th = Thread(target=subprocess.call, args="startx".split())
    th.daemon = True
    th.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logger.warning("exit by KeyboardInterrupt")
        sys.exit(0)
    finally:
        # nfc_issuer.stop()
        qr_issuer.stop()

if __name__ == '__main__':
    main(sys.argv)
