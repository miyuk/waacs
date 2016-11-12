# -*- coding: utf-8 -*-

import logging
logger = logging.getLogger(__name__)
import MySQLdb as db
from datetime import datetime, timedelta
import json
import random
import falcon
from OpenSSL import crypto
import subprocess
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


def make_cert_req(type, bits, C, ST, O, CN):
    key = crypto.PKey()
    key.generate_key(type, bits)
    req = crypto.X509Req()
    sbj = req.get_subject()
    sbj.C = C
    sbj.ST = ST
    sbj.O = O
    sbj.CN = CN
    req.set_pubkey(key)
    return req, key


class RequestWifiAuthApi(object):

    @property
    def db_conn_args(self):
        return {"user": self.user, "passwd": self.passwd, "db": self.db, "host": self.host}

    def __init__(self, host, user, passwd, db, certs_dir):
        self.host = host
        self.user = user
        self.passwd = passwd
        self.db = db
        self.certs_dir = certs_dir

    def on_get(self, req, resp, ssid, token):
        with db.connect(**self.db_conn_args) as cur:
            cur.execute(
                "SELECT COUNT(*) FROM token WHERE token = %s", (token, ))
            if not cur.fetchone():
                logger.warning("not found token: %s", token)
                resp.status = falcon.HTTP_401
                return
            while True:
                user_id = "".join([random.choice(api.SOURCE_CHAR)
                                   for x in range(10)])
                cur.execute(
                    "SELECT COUNT(*) FROM user WHERE user_id = %s", (user_id, ))
                if cur.fetchone()[0] == 0:
                    break
            password = "".join([random.choice(api.SOURCE_CHAR)
                                for x in range(10)])
            now = datetime.now()
            cur.execute("INSERT INTO user(user_id, password, issuance_time) VALUES(%s, %s, %s)",
                        (user_id, password, now.strftime("%Y-%m-%d %H:%M:%S")))
        req, key = make_cert_req(
            crypto.TYPE_RSA, 2048, "Osaka", "Osaka", "Osaka Institute of Technology", user_id)

        subprocess.call("pushd {0}".format(self.certs_dir).split())
        with open("./client.csr", "w") as f:
            f.write(crypto.dump_certificate_request(crypto.FILETYPE_TEXT, req))
        with open("./client.key", "w") as f:
            f.write(crypto.dump_privatekey(crypto.FILETYPE_PEM, key))
        subprocess.call(
            "make client.pem USER_NAME={0}".format(user_id).split())
        os.rename("{0}.pem".format(user_id), "./waacs/")
        subprocess.call("popd".split())
        if "iPhone" in req.user_agent:
            resp.content_type = MIMETYPE_MOBILECONFIG
            config = make_mobileconfig(ssid, user_id, password)
            resp.body = config
        elif "Android" in req.user_agent:
            resp.content_type = MIMETYPE_WAACSCONFIG
            config = make_waacsconfig(ssid, user_id, password)
            resp.body = config
        else:
            resp.status = falcon.HTTP_401
            resp.body = "This system is iPhone and Android only"
