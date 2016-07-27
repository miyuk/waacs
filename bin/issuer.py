#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os
sys.path.insert(1, os.path.dirname(sys.path[0]))
import waacs
from waacs.nfc import NfcConnection
from waacs.tls import TlsClient, TlsListener
import ConfigParser
import threading
import time
import nfc
import nfc.ndef
import logging
import logging.config
logger = logging.getLogger(__name__)
import json


config = ConfigParser.SafeConfigParser()
config.read(os.path.join(sys.path[0], "issuer.cfg"))
config = ConfigParser.SafeConfigParser()
config.read(os.path.join(sys.path[0], "issuer.cfg"))
ssid = config.get("NfcConnection", "ssid")
issuer_id = config.get("IssuerAuth", "issuer_id")
issuer_password = config.get("IssuerAuth", "issuer_password")
server_address = config.get("TlsClient", "server_address")
server_port = config.getint("TlsClient", "server_port")


def main(argc, argv):
    log_init()
    nfc_conn = NfcConnection()
    while True:
        if not nfc_conn.connect():
            logger.warn("can't connect NFC")
            continue
        param = issue_user()
        json = param.to_json()
        nfc_conn.send_waacs_message(json)
        nfc_conn.close()
        raw_input()


def issue_user():
    # serverに接続
    # TODO: 失敗してもなにか送る
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
        logger.warn("can't login")
    client.close()
    param = waacs.Parameter()
    param.user_id = user_id
    param.ssid = ssid
    param.password = password
    param.issuance_time = issuance_time
    param.expiration_time = expiration_time
    return param


def log_init():
    cfg_file = os.path.join(sys.path[0], "issuer_log.cfg")
    logging.config.fileConfig(cfg_file)

if __name__ == '__main__':
    argv = sys.argv
    main(len(argv), argv)
