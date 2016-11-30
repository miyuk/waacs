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
        self.ca_crt = crypto.load_certificate(
            crypto.FILETYPE_PEM, open(os.path.join(self.certs_dir, "ca.pem")).read())
        self.ca_key = crypto.load_privatekey(
            crypto.FILETYPE_PEM, open(os.path.join(
                self.certs_dir, "ca.pem").read(), "waacs"))
        self.C = "JP"
        self.ST = "Osaka"
        self.O = "Osaka Institute of Technology"
        self.encryption_type = crypto.TYPE_RSA
        self.key_size = 2048
        self.expiration_time = 60 * 60

    def on_get(self, req, resp, ssid, token):
        now = datetime.now()
        if "iPhone" in req.user_agent or "iPad" in req.user_agent:
            device_type = "iOS"
        elif "Android" in req.user_agent:
            device_type = "Android"
        else:
            resp.status = falcon.HTTP_401
            resp.body = "This system is iPhone and Android only"
            return
        with db.connect(**self.db_conn_args) as cur:
            rownum = cur.execute(
                "SELECT access_issuer_id, token_issuance_time　FROM token WHERE token = %s", (token, ))
            if not rownum:
                logger.warning("not found token: %s", token)
                resp.status = falcon.HTTP_401
                return
            access_issuer_id, token_issuance_time = cur.fetchone()
            # TODO
            if now - token_issuance_time > timedelta(seconds=60):
                logger.warning("expiration token: %s", token)
                resp.status = falcon.HTTP_401
                return
            cur.execute("DELETE FROM token WHERE token = %s", (token, ))
            user_id, password = self.gen_credential(cur)
            eap_type = "EAP-TLS" if device_type == "iOS" else "EAP_TTLS"
            cur.execute("INSERT INTO user(user_id, password, issuance_time, access_issuer_id, eap_type) VALUES(%s, %s, %s, %s, %s)",
                        (user_id, password, api.format_time(now), access_issuer_id, device_type))
            cur.execute("SELECT LAST_INSERT_ID() FROM user")
            serial = cur.fetchone()[0]
            p12 = self.gen_certificate(
                cur, serial, user_id, password)
            cur.execute("INSERT INTO certificate(id, cert_filename) VALUES(%d, %s)",
                        serial, os.path.join(self.certs_dir, user_id + ".p12"))
            logger.debug(
                "create credential user_id: %s password: %s", user_id, password)
            if device_type == "iOS":
                resp.content_type = MIMETYPE_MOBILECONFIG
                config = make_mobileconfig_tls(ssid, user_id, crt, "waacs")
                resp.body = config
            elif device_type == "Android"
                resp.content_type = MIMETYPE_WAACSCONFIG
                config = make_waacsconfig_ttls(ssid, user_id, password)
                resp.body = config

    def gen_credential(self, cur):
        while True:
            user_id = "".join([random.choice(api.SOURCE_CHAR)
                               for x in range(32)])
            cur.execute(
                "SELECT TRUE FROM user WHERE user_id = %s", (user_id, ))
            if cur.fetchone():
                break
        password = "".join([random.choice(api.SOURCE_CHAR)
                            for x in range(32)])
        cur.execute("INSERT INTO user(user_id, password, issuance_time) VALUES(%s, %s, %s)",
                    (user_id, password, api.format_time(now)))
        return user_id, password

    def gen_certificate(self, cur, sefial, user_id, passphrase):
        key = crypto.PKey()
        key.generate_key(self.encryption_type, self.key_size)
        crt = crypto.X509()
        sbj = crt.get_subject()
        sbj.C = self.C
        sbj.ST = self.ST
        sbj.O = self.O
        sbj.CN = user_id
        crt.gmtime_adj_notBefore(0)
        crt.gmtime_adj_notAfter(self.expiration_time)
        crt.set_serial_number(serial)
        crt.set_issuer(ca_crt.get_subject())
        crt.set_pubkey(key)
        crt.sign(ca_key, "sha256")
        p12 = crypto.PKCS12()
        p12.set_privatekey(key)
        p12.set_certificate(crt)
        p12.set_ca_certificates(self.ca_key)
        return p12.export(passphrase)
