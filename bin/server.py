#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os
sys.path.insert(1, os.path.dirname(sys.path[0]))
import waacs
from waacs.db import UserDB
from waacs.tls import TlsClient, TlsListener
import ConfigParser
import threading
import socket
import logging
import logging.config
logger = logging.getLogger(__name__)
import json


config = ConfigParser.SafeConfigParser()
config.read(os.path.join(sys.path[0], "server.cfg"))
listen_address = config.get("TlsServer", "listen_address")
listen_port = config.getint("TlsServer", "listen_port")
server_cert = config.get("TlsServer", "server_cert")
server_key = config.get("TlsServer", "server_key")
ca_certs = config.get("TlsServer", "ca_certs")
db_host = config.get("UserDB", "host")
db_user = config.get("UserDB", "user")
db_passwd = config.get("UserDB", "password")


def main(argc, argv):
    log_init()
    db = UserDB(db_host, db_user, db_passwd)
    listener = TlsListener(
        listen_address, listen_port, server_cert, server_key, ca_certs)
    listener.start()
    while True:
        client = listener.accept()
        # issuerからの取得データはすべてJSON形式
        data = client.read()
        request = json.loads(data)
        # REQUEST_USERならユーザ発行
        if request["action"] == "REQUEST_USER":
            issuer_id = request["issuerId"]
            issuer_password = request["issuerPassword"]
            res_dict = dict()
            if not db.check_issuer(issuer_id, issuer_password):
                res_dict["status"] = "FAIL"
                client.write(json.dumps(res_dict))
                client.close()
                continue
            user_id, password, issuance_time, expiration_time = issue_user(
                db, issuer_id)
            res_dict["status"] = "OK"
            res_dict["userId"] = user_id
            res_dict["password"] = password
            res_dict["issuanceTime"] = waacs.format_time(issuance_time)
            res_dict["expirationTime"] = waacs.format_time(
                expiration_time)
            client.write(json.dumps(res_dict))
            client.close()


def issue_user(db, issuer_id):
    # ランダムなユーザ名とパスワードを作成のみ
    user_id, password = db.create_user()
    # データベースに登録する
    issuance_time, expiration_time = db.issue_user(
        user_id, password, issuer_id)
    return (user_id, password, issuance_time, expiration_time)


def log_init():
    cfg_file = os.path.join(sys.path[0], "server_log.cfg")
    logging.config.fileConfig(cfg_file)
    # loglevel = logging.DEBUG
    # format = "%(asctime)8s.%(msecs)03d|[%(name)s %(lineno)d(%(levelname)s)] %(message)s"
    # date_format = "%H:%M:%S"
    # logging.basicConfig(level=loglevel,
    #                     format=format,
    #                     datefmt=date_format)

if __name__ == '__main__':
    argv = sys.argv
    main(len(argv), argv)
