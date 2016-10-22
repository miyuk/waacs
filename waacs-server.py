#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os
from ConfigParser import SafeConfigParser
import json
import logging
from logging.config import fileConfig
fileConfig(os.path.join(sys.path[0], "config/server_log.cfg"))
logger = logging.getLogger(__name__)
import falcon
from wsgiref import simple_server
import api

config = SafeConfigParser()
config.read(os.path.join(sys.path[0], "config/server.cfg"))
listen_address = config.get("ApiServer", "listen_address")
listen_port = config.getint("ApiServer", "listen_port")

db_host = config.get("UserDB", "host")
db_user = config.get("UserDB", "user")
db_passwd = config.get("UserDB", "password")


def main(argv):
    requestwifi_api = api.RequestWifiApi()
    downloadmobileconfig_api = api.DownloadMobleconfigApi()
    issuetoken_api = api.IssueTokenApi()
    app = falcon.API()
    app.add_route("/request_wifi/{token}", requestwifi_api)
    app.add_route("/download_mobileconfig/{ssid}/{user_id}/{password}/", downloadmobileconfig_api)
    app.add_route("/issue_token/", issuetoken_api)
    httpd = simple_server.make_server(listen_address, listen_port, app)
    th = Thread(target=httpd.serve_forever)
    th.daemon = True
    th.start()
    while True:
        pass

if __name__ == '__main__':
    main(sys.argv)
