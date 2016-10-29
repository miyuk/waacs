# -*- coding: utf-8 -*-

import logging
logger = logging.getLogger(__name__)
import MySQLdb as db
from datetime import datetime, timedelta
import json
import random
import api


MIMETYPE_MOBILECONFIG = "application/x-apple-aspen-config"
MIMETYPE_WAACSCONFIG = "application/x-waacs-config"

templete_file_path = "./template.mobileconfig"


def make_mobileconfig(ssid, user_id, password):
    config = open(templete_file_path).read()
    return config.replace("$ssid", ssid).replace("$userId", user_id).replace("$password", password)


def make_waacsconfig(ssid, user_id, password):
    config = {"ssid": ssid, "userId": user_id, "password": password}
    return json.dumps(config)


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
            cur.execute("SELECT COUNT(*) FROM token WHERE token = %s", (token, ))
            if not cur.fetchone():
                logger.warning("not found token: %s", token)
                resp.status = falcon.HTTP_401
                return
            while True:
                user_id = "".join([random.choice(api.SOURCE_CHAR) for x in range(10)])
                cur.execute("SELECT COUNT(*) FROM user WHERE user_id = %s", (user_id, ))
                if cur.fetchone()[0] == 0:
                    break
            password = "".join([random.choice(api.SOURCE_CHAR) for x in range(10)])
            now = datetime.now()
            cur.execute("INSERT INTO user(user_id, password, issuance_time) VALUES(%s, %s, %s)",
                        (user_id, password, now.strftime("%Y-%m-%d %H:%M:%S")))
        if "iPhone" in req.user_agent or True:
            resp.content_type = MIMETYPE_MOBILECONFIG
            config = make_mobileconfig(ssid, user_id, password)
            resp.body = config
        elif "Android" in req.user_agent:
            resp.content_type = MIMETYPE_WAACS
            config = make_waacsconfig(ssid, user_id, password)
            resp.body = config
