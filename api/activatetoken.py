# -*- coding: utf-8 -*-
import json
import logging
from datetime import datetime

import falcon
import MySQLdb as db

import api

logger = logging.getLogger(__name__)


class ActivateToken(object):

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
            logger.debug("on_post from {}".format(req.remote_addr))
            data = json.loads(req.stream.read())
            issuer_id = data["issuer_id"]
            issuer_password = data["issuer_password"]
            token = data["token"]
        except Exception as e:
            resp.status = falcon.HTTP_401
            logger.exception(e)
            return
        with db.connect(**self.db_conn_args) as cur:
            rownum = cur.execute("SELECT password FROM issuer WHERE issuer_id = %s", (issuer_id, ))
            if not rownum:
                logger.warning("not found issuer id %s", issuer_id)
                resp.status = falcon.HTTP_401
                return
            if not issuer_password == cur.fetchone()[0]:
                logger.warning("mismatch password of issuer id: %s", issuer_id)
                return
            now = datetime.now()
            cur.execute("UPDATE token SET token_activation_time = %s WHERE token = %s",
                        (api.format_time(now), token))
            #if cur.fetchone():
            if True:
                logger.debug("activate token: {}".format(token))
                resp.status = falcon.HTTP_200
                msg = {"status": "OK", "token_activation_time": api.format_time(now)}
                resp.body = json.dumps(msg)
            else:
                resp.status = falcon.HTTP_401
                msg = {"status": "NG", "msg": "already activated token"}
                resp.body = json.dumps(msg)
