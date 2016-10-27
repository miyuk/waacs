# -*- coding: utf-8 -*-

import logging
logger = logging.getLogger(__name__)
import MySQLdb as db
from datetime import datetime, timedelta
import json
import random
import api


class RequestWifiAuthApi(object):

    @property
    def db_conn_args(self):
        return {"user": self.user, "passwd": self.passwd, "db": self.db, "host": self.host}

    def __init__(self, host, user, passwd, db):
        self.host = host
        self.user = user
        self.passwd = passwd
        self.db = db

    def on_get(self, req, resp, token):
        with db.connect(**self.db_conn_args) as cur:
            cur.execute("SELECT COUNT(*) FROM token WHERE token = %s", token)
            if not cur.fetchone():
                logger.warning("not found token: %s", token)
                resp.status = falcon.HTTP_401
                return
            while True:
                user_id = "".join([random.choice(api.SOURCE_CHAR) for x in range(10)])
                cur.execute("SELECT COUNT(*) FROM user WHERE user_id = %s", user_id)
                if cur.fetchone()[0] == 0:
                    break
            password = "".joing([random.choice(api.SOURCE_CHAR) for x in range(10)])
            cur.execute("INSERT INTO user(user_id, password, issuance_time) VALUES(%s, %s, %s)",
                        user_id, password, now.strftime("%Y-%m-%d %H:%M:%S"))
        if "iPhone" in req.user_agent or True:
            resp.status = falcon.HTTP_301
            resp.location = "/download_mobileconfig/{0}/".format(user_id)
        elif "android" in req.user_agent:
            pass
