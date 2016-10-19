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

HOST = "localhost"
USER = "waacs"
PASSWD = "waacs"
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

    @property
    def db_conn_args(self):
        return {"user": self.ueer, "passwd": self.passwd, "db": self.waacs, "host": self.localhost}

    def __init__(self, host, user, passwd, db):
        self.host = host
        self.user = user
        self.passwd = passwd
        self.db = db

    # @falcon.before(before)
    # @falcon.after(after)
    def on_get(self, req, resp, token):
        with db.connect(**Self.db_conn_arg) as cur:
            cur.execute("SELECT user_id FROM token WHERE token = %s", token)
            user_id = cur.fetchone()[0]
            if not user_id:
                logger.warning("not found token: %s", token)
                resp.status = falcon.HTTP_401
                return
        if "iPhone" in req.user_agent or True:
            resp.status = falcon.HTTP_301
            resp.location = "/download_mobileconfig/{0}/".format(user_id)


class DownloadMobleconfigApi(object):

    def on_get(self, req, resp, user_id):
        resp.content_type = "application/x-apple-aspen-config"
        config = open(file_path).read()
        config = config.replace("$userId", user_id).replace("$userPassword", userId)
        resp.body = config


class IssueTokenApi(object):

    def on_post(self):


def main(argv):
    app = falcon.API()
    app.add_route("/qr_scan/{token}", QrScanApi(HOST, USER, PASSWD, DB)
    app.add_route("/download_mobileconfig/{user_id}/", DownloadMobleconfigApi())
    httpd=simple_server.make_server("150.89.94.224", 80, app)
    th=Thread(target=httpd.serve_forever)
    th.daemon=True
    th.start()
    while(True):
        pass

if __name__ == "__main__":
    main(sys.argv)
