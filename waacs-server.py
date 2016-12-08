#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import logging
import os
import sys
import time
from ConfigParser import SafeConfigParser
from logging.config import fileConfig
from threading import Thread

import falcon

from api import IssueTokenApi, RequestWifiAuthApi
from wsgiref.simple_server import WSGIRequestHandler, make_server

logger = logging.getLogger(__name__)

fileConfig(os.path.join(sys.path[0], "config/server_log.cfg"))
config = SafeConfigParser()
config.read(os.path.join(sys.path[0], "config/server.cfg"))
api_conf_dict = dict(config.items("ApiServer"))
listen_address = api_conf_dict["listen_address"]
listen_port = api_conf_dict["ApiServer", "listen_port"]
db_conf_dict = dict(config.items("UserDB"))
db_host = db_conf_dict["host"]
db_user = db_conf_dict["user"]
db_passwd = db_conf_dict["password"]
db_db = db_conf_dict["db"]
pki_conf_dict = dict(config.items("PKI"))
ca_crt = pki_conf_dict["ca_crt"]
ca_key = pki_conf_dict["ca_key"]
client_crt_dir = pki_conf_dict["client_crt_dir"]
common_name = pki_conf_dict["CN"]
state = pki_conf_dict["ST"]
organization = pki_conf_dict["O"]
expiration_time = pki_conf_dict["expiration_time"]
key_size = pki_conf_dict["key_size"]
encryption_type = pki_conf_dict["encryption_type"]


def main(argv):
    requestwifi_api = RequestWifiAuthApi(db_conf_dict, pki_conf_dict)
    issuetoken_api = IssueTokenApi(db_conf_dict)
    app = falcon.API()
    app.add_route("/request_wifi_auth/{ssid}/{token}", requestwifi_api)
    app.add_route("/issue_token/", issuetoken_api)

    class QuietHandler(WSGIRequestHandler):

        def log_request(*args, **kw):
            if args[1] != "200":
                logger.warning("%s: %s", args[1], args[0].path)
    httpd = make_server(listen_address, listen_port,
                        app, handler_class=QuietHandler)
    th = Thread(target=httpd.serve_forever)
    th.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logger.warning("exit by keyboardInterrupt")
        sys.exit(0)
    finally:
        httpd.shutdown()
        th.join()


if __name__ == '__main__':
    main(sys.argv)
