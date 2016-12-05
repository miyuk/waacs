#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os
from ConfigParser import SafeConfigParser
import json
import logging
from logging.config import fileConfig

from wsgiref.simple_server import make_server, WSGIRequestHandler
from threading import Thread
import falcon
import time
import api
logger = logging.getLogger(__name__)

fileConfig(os.path.join(sys.path[0], "config/server_log.cfg"))
config = SafeConfigParser()
config.read(os.path.join(sys.path[0], "config/server.cfg"))
api_conf_dict = dict(config.sections("ApiServer"))
listen_address = api_conf_dict["listen_address"]
listen_port = api_conf_dict["ApiServer", "listen_port"]
db_conf_dict = dict(config.sections("UserDB"))
db_host = db_conf_dict["host"]
db_user = db_conf_dict["user"]
db_passwd = db_conf_dict["password"]
db_db = db_conf_dict["db"]
certs_dir = config.get("Certs", "certs_dir")


def main(argv):
    requestwifi_api = api.RequestWifiAuthApi(db_conf_dict, certs_dir)
    issuetoken_api = api.IssueTokenApi(db_conf_dict)
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
