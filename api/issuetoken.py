# -*- coding: utf-8 -*-
import json
import logging
import random
from datetime import datetime

import falcon
import MySQLdb as db

import api

logger = logging.getLogger(__name__)


class IssueTokenApi(object):

    @property
    def db_conn_args(self):
        return {"user": self.user, "passwd": self.passwd, "db": self.db, "host": self.host}

    def __init__(self, db_conf):
        self.host = db_conf["host"]
        self.user = db_conf["user"]
        self.passwd = db_conf["passwd"]
        self.db = db_conf["db"]

    def on_post(self, req, resp):
        try:
            data = json.loads(req.stream.read())
            issuer_id = data["issuer_id"]
            issuer_password = data["issuer_password"]
            access_type = data["access_type"]
            association_ssid = data["association_ssid"]
            logger.debug("on_post for ssid %s by %s", association_ssid, access_type)
        except Exception as e:
            logger.exception(e)
            resp.status = falcon.HTTP_401
            return
        with db.connect(**self.db_conn_args) as cur:
            logger.debug("issuer authentication: (id: %s, password: %s)",
                         issuer_id, issuer_password)
            rownum = cur.execute(
                "SELECT password FROM issuer WHERE issuer_id = %s", (issuer_id, ))
            if not rownum:
                logger.warning("not found issuer id %s", issuer_id)
                resp.status = falcon.HTTP_401
                return
            if not issuer_password == cur.fetchone()[0]:
                logger.warning("mismatch password of issuer id: %s", issuer_id)
                return
                logger.debug("issuer authentication is passed")
            while True:
                token = "".join([random.choice(api.SOURCE_CHAR)
                                 for x in range(32)])
                cur.execute("SELECT TRUE FROM token WHERE token = %s", (token, ))
                if not cur.fetchone():
                    break
            now_str = api.format_time(datetime.now())
            cur.execute("INSERT INTO token(token, token_issuance_time, access_issuer_id, \
                         access_type, association_ssid) VALUES(%s, %s, %s, %s, %s)",
                        (token, now_str, issuer_id, access_type, association_ssid))
            cur.execute("INSERT IGNORE INTO log (token, token_issu_time) VALUES(%s, %s)",
                        (token, now_str))
        logger.debug("issue token success")
        msg = {"token": token, "token_issuance_time": now_str}
        resp.body = json.dumps(msg)
