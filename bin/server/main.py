#!/usr/bin/python
# -*- coding: utf-8 -*-
import sys
import os
lib_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(1, lib_dir)
from waacs import userdb, tlslistener, stringutils
import ConfigParser
import threading
import socket
import logging
logger = logging.getLogger(__name__)
import json


os.chdir(os.path.dirname(os.path.abspath(__file__)))
config = ConfigParser.ConfigParser()
config.read("./server.cfg")
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
    db = userdb.UserDB(db_host, db_user, db_passwd)
    listener = tlslistener.TlsListener(listen_address, listen_port, server_cert, server_key, ca_certs)
    listener.start()
    while True:
        client = listener.accept()
        data = client.read()
        request = json.loads(data)
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
            res_dict["issuanceTime"] = stringutils.format_time(issuance_time)
            res_dict["expirationTime"] = stringutils.format_time(expiration_time)
            client.write(json.dumps(res_dict))
            client.close()

def issue_user(db, issuer_id):
        #ランダムなユーザ名とパスワードを作成のみ
        user_id, password = db.create_user()
        #データベースに登録する
        issuance_time, expiration_time = db.issue_user(user_id, password, issuer_id)
        return (user_id, password, issuance_time, expiration_time)


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