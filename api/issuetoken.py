# -*- coding: utf-8 -*-

import logging
logger = logging.getLogger(__name__)
import MySQLdb as db
from datetime import datetime, timedelta
import json
import random


class IssueTokenApi(object):

    @property
    def db_conn_args(self):
        return {"user": self.user, "passwd": self.passwd, "db": self.db, "host": self.host}

    def __init__(self, host, user, passwd, db):
        self.host = host
        self.user = user
        self.passwd = passwd
        self.db = db

    def on_post(self, req, resp):
        try:
            data = json.loads(req.stream.read())
            issuer_id = data["issuer_id"]
            issuer_password = data["issuer_password"]
        except Exception as e:
            resp.status = falcon.HTTP_401
            return
        with db.connect(**self.db_conn_args) as cur:
            cur.execute("SELECT password FROM issuer WHERE issuer_id = %s", issuer_id)
            ref_issuer_password = cur.featchone()[0]
            if not ref_issuer_password:
                logger.warning("not found issuer id: %s", issuer_id)
                resp.status = falcon.HTTP_401
                return
            if not issuer_password == ref_issuer_password:
                logger.warning("mismatch password of issuer id: %s", issuer_id)
                return
            while True:
                token = "".join([random.choice(SOURCE_CHAR) for x in range(10)])
                if not cur.execute("SELECT COUNT(*) FROM token WHERE token = %s", token):
                    break
            now = datetime.now()
            cur.execute("INSERT INTO token(token, token_issuance_time) VALUES(%s, %s)",
                        token, now.strftime("%Y-%m-%d %H:%M:%S"))
        msg = {"token": token, "issuance_time": now.strftime("%Y-%m-%d %H:%M:%S")}
        resp.body = json.dumps(msg)
