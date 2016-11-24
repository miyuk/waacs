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
import os
import os.path
import base64
import api
from parameter import Parameter, TlsParameter, TtlsParameter, TYPE_TLS, TYPE_TTLS

MIMETYPE_MOBILECONFIG = "application/x-apple-aspen-config"
MIMETYPE_WAACSCONFIG = "application/x-waacs-config"

templete_ttls_file_path = "./template_ttls.mobileconfig"
templete_tls_file_path = "./template_tls.mobileconfig"


def make_mobileconfig_ttls(ssid, user_id, password):
    config = open(templete_ttls_file_path).read()
    return config.replace("$ssid", ssid).replace("$userId", user_id).replace("$password", password)


def make_mobileconfig_tls(ssid, cert_name, cert_content, cert_pass, expiration_time):
    config = open(templete_tls_file_path).read()
    cert_format_content = base64.encodestring(cert_content)
    remaining_seconds = (expiration_time - datetime.now()).seconds
    return config.replace("$ssid", ssid).replace("$cert_name", cert_name,)\
        .replace("$cert_content", cert_format_content).replace("$cert_pass", cert_pass)\
        .replace("$remaining_seconds", remaining_seconds)


def make_waacsconfig_ttls(ssid, user_id, password):
    param = Parameter()
    param.ssid = ssid
    param.eap_type = TYPE_TTLS
    ttls = TtlsParameter()
    ttls.user_id = user_id
    ttls.password = password
    param.ttls_parameter = ttls
    return json.dumps(param.to_dict())


def make_waacsconfig_tls(ssid, cert_name, cert_content, cert_pass):
    param = Parameter()
    param.ssid = ssid
    param.eap_type = TYPE_TLS
    tls = TlsParameter()
    tls.client_certificate_name = cert_name
    tls.client_certificate_content = cert_content
    tls.passphrase = cert_pass
    param.tls_parameter = tls
    return json.dumps(param.to_dict())


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
    req.sign(key, "sha256")
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

        csr, key = make_cert_req(
            crypto.TYPE_RSA, 2048, "JP", "Osaka", "Osaka Institute of Technology", user_id)
        last_dir = os.path.realpath(os.getcwd())
        os.chdir(self.certs_dir)
        with open("./client.csr", "w") as f:
            f.write(crypto.dump_certificate_request(crypto.FILETYPE_PEM, csr))
        with open("./client.key", "w") as f:
            f.write(crypto.dump_privatekey(crypto.FILETYPE_PEM, key))
        with open(os.devnull) as devnull:
            subprocess.call("make client.p12".split(), stdout=devnull)
            os.rename("client.p12", "./waacs/{0}.p12".format(user_id))
            crt = open("./waacs/{0}.p12".format(user_id)).read()
            subprocess.call("make clean".split(), stdout=devnull)
            passphrase = "waacs"  # TODO
        os.chdir(last_dir)
        if "iPhone" in req.user_agent or "iPad" in req.user_agent:
            resp.content_type = MIMETYPE_MOBILECONFIG
            # config = make_mobileconfig_ttls(ssid, user_id, password)
            config = make_mobileconfig_tls(ssid, user_id, crt, passphrase)
            resp.body = config
        elif "Android" in req.user_agent:
            resp.content_type = MIMETYPE_WAACSCONFIG
            # config = make_waacsconfig_ttls(ssid, user_id, password)
            config = make_waacsconfig_tls(ssid, user_id, crt, passphrase)
            resp.body = config
        else:
            resp.status = falcon.HTTP_401
            resp.body = "This system is iPhone and Android only"
