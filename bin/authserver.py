#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import sys
import json
from wsgiref import simple_server
import falcon
import logging
logging.basicConfig()
logger = logging.getLogger(__name__)
logger.level = logging.DEBUG
import MySQLdb as db
import random
from datetime import datetime, timedelta
import pdb
from threading import Thread
file_path = "sample.mobileconfig"

DB = "waacs"
USER_TBL = "user"
DEVICE_TBL = "user_device"
ISSUER_TBL = "issuer"
SOURCE_CHAR = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"


def before(req, res, resource, params):
    logger.debug("*****before*****")
    logger.debug("\n".join(k + "=" + v for k, v in req.headers.items()))
    logger.debug(resource)
    logger.debug(params)


def after(req, res, resource):
    logger.debug("*****after*****")
    logger.debug("\n".join(k + "=" + v for k, v in res._headers.items()))


class QrScanApi(object):

    def __init__(self):
        self.db_conn_args = {}
        self.db_conn_args["user"] = "waacs"
        self.db_conn_args["passwd"] = "waacs"
        self.db_conn_args["db"] = "waacs"
        self.db_conn_args["host"] = "localhost"

    @falcon.before(before)
    @falcon.after(after)
    def on_get(self, req, resp, token):
        if "iPhone" in req.user_agent:
            resp.status = falcon.HTTP_301
            resp.location = "/download_mobileconfig/{0}/".format(token)
        with db.connect(**self.db_conn_args) as cursor:


class DownloadMobleconfigApi(object):

    def on_get(self, req, resp, userId):
        resp.content_type = "application/x-apple-aspen-config"
        config = open(file_path).read()
        config = config.replace("$userId", userId)
        resp.body = config


def main(argv):
    app = falcon.API()
    app.add_route("/qr_scan/{token}", QrScanApi())
    app.add_route("/download_mobileconfig/{userId}/", DownloadMobleconfigApi())
    httpd = simple_server.make_server("150.89.94.224", 80, app)
    th = Thread(target=httpd.serve_forever)
    th.daemon = True
    th.start()
    while(True):
        pass

if __name__ == "__main__":
    main(sys.argv)
