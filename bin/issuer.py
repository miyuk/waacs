#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os
sys.path.insert(1, os.path.dirname(sys.path[0]))
from ConfigParser import SafeConfigParser
import json
import logging
from logging.config import fileConfig
logger = logging.getLogger(__name__)
import qrcode
import time
import waacs
from waacs.nfc import NfcConnection
from waacs.tls import TlsClient, TlsListener

config = SafeConfigParser()
config.read(os.path.join(sys.path[0], "config/issuer.cfg"))
ssid = config.get("NfcConnection", "ssid")
android_package_name = config.get("NfcConnection", "android_package_name")
issuer_id = config.get("IssuerAuth", "issuer_id")
qr_output_path = config.get("Qrcode", "output_path")
issuer_password = config.get("IssuerAuth", "issuer_password")
server_address = config.get("TlsClient", "server_address")
server_port = config.getint("TlsClient", "server_port")
cfg_file = os.path.join(sys.path[0], "config/issuer_log.cfg")
logging.config.fileConfig(cfg_file)


def main(args):
    # nfc_conn = NfcConnection()
    is_stop = False
    while not is_stop:
        param = issue_user()
        qr = qrcode.make(param)
        qr.save(qr_output_path)
        time.sleep(1)
        # try:
        #     if not nfc_conn.connect():
        #         logger.error("NFC connection error")
        #         sys.exit(1)
        #     param = issue_user()
        #     json = param.to_json()
        #     nfc_conn.send_waacs_message(json, android_package_name)
        # except KeyboardInterrupt as e:
        #     Log.warn("exit by KeybordInterrupt")
        #     is_stop = True
        # finally:
        #     nfc_conn.close()
    sys.exit(0)


def issue_user():
    # serverに接続
    client = TlsClient()
    client.connect(server_address, server_port)
    request = dict()
    request["action"] = "REQUEST_USER"
    request["issuerId"] = issuer_id
    request["issuerPassword"] = issuer_password
    json_text = json.dumps(request)
    client.write(json_text)
    data = client.read()
    response = json.loads(data)
    # reponseのstatusがOKならパラメータを取得して返す
    if response["status"] == "OK":
        user_id = response["userId"]
        password = response["password"]
        issuance_time = waacs.parse_time(response["issuanceTime"])
        expiration_time = waacs.parse_time(response["expirationTime"])
    else:
        logger.warn("server login password is wrong")
    client.close()
    param = waacs.Parameter()
    param.user_id = user_id
    param.ssid = ssid
    param.password = password
    param.issuance_time = issuance_time
    param.expiration_time = expiration_time
    return param

if __name__ == '__main__':
    main(sys.argv)
