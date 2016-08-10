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
import waacs
from waacs.db import UserDB
from waacs.tls import TlsListener


config = SafeConfigParser()
config.read(os.path.join(sys.path[0], "config/server.cfg"))
listen_address = config.get("TlsServer", "listen_address")
listen_port = config.getint("TlsServer", "listen_port")
server_cert = config.get("TlsServer", "server_cert")
server_key = config.get("TlsServer", "server_key")
ca_certs = config.get("TlsServer", "ca_certs")
db_host = config.get("UserDB", "host")
db_user = config.get("UserDB", "user")
db_passwd = config.get("UserDB", "password")
cfg_file = os.path.join(sys.path[0], "config\server_log.cfg")
fileConfig(cfg_file)


def main(args):
    db = UserDB(db_host, db_user, db_passwd)
    listener = TlsListener(listen_address, listen_port, server_cert, server_key, ca_certs)
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
            user_id, password, issuance_time, expiration_time = issue_user(db, issuer_id)
            res_dict["status"] = "OK"
            res_dict["userId"] = user_id
            res_dict["password"] = password
            res_dict["issuanceTime"] = waacs.format_time(issuance_time)
            res_dict["expirationTime"] = waacs.format_time(expiration_time)
            client.write(json.dumps(res_dict))
            client.close()


def issue_user(db, issuer_id):
    # ランダムなユーザ名とパスワードを作成のみ
    user_id, password = db.create_user()
    # データベースに登録する
    issuance_time, expiration_time = db.issue_user(
        user_id, password, issuer_id)
    return (user_id, password, issuance_time, expiration_time)


if __name__ == '__main__':
    main(sys.argv)
