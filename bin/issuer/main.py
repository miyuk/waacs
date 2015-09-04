#!/usr/bin/python
# -*- coding: utf-8 -*-
import sys
import os
lib_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(1, lib_dir)
import waacs
from waacs import nfcclient, nfcserver, nfcconnection, parameter, tlsclient, stringutils
import ConfigParser
import threading
import time
import nfc
import nfc.ndef
import logging
logger = logging.getLogger(__name__)
import json


os.chdir(os.path.dirname(os.path.abspath(__file__)))
config = ConfigParser.SafeConfigParser()
config.read("./issuer.cfg")
ssid = config.get("NfcConnection", "ssid")
issuer_id = config.get("IssuerAuth", "issuer_id")
issuer_password = config.get("IssuerAuth", "issuer_password")
server_address = config.get("TlsClient", "server_address")
server_port = config.getint("TlsClient", "server_port")

def main(argc, argv):
    log_init()
    nfc_conn = nfcconnection.NfcConnection()
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
    client = tlsclient.TlsClient()
    client.connect(server_address, server_port)
    request = dict()
    request["action"] = "REQUEST_USER"
    request["issuerId"] = issuer_id
    request["issuerPassword"] = issuer_password
    json_text = json.dumps(request)
    client.write(json_text)
    data = client.read()
    response = json.loads(data)
    if response["status"] == "OK":
        user_id = response["userId"]
        password = response["password"]
        issuance_time = stringutils.parse_time(response["issuanceTime"])
        expiration_time = stringutils.parse_time(response["expirationTime"])
    else:
        logger.warn("can't login")
    client.close()
    param = parameter.Parameter()
    param.user_id = user_id
    param.ssid = ssid
    param.password = password
    param.issuance_time = issuance_time
    param.expiration_time = expiration_time
    return param

def log_init():
    loglevel = logging.DEBUG
    format = "%(asctime)8s.%(msecs)03d|[%(name)s %(lineno)d(%(levelname)s)] %(message)s"
    date_format = "%H:%M:%S"
    logging.basicConfig(level=loglevel,
        format=format,
        datefmt=date_format)

if __name__ == '__main__':
    argv = sys.argv
    main(len(argv), argv)
