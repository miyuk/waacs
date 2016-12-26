# -*- coding: utf-8 -*-

import base64
import json
import logging
import os
import os.path
import random
from datetime import datetime

import falcon
import MySQLdb as db
from OpenSSL import crypto
from pytz import timezone

import api
from parameter import (TYPE_TLS, TYPE_TTLS, Parameter, TlsParameter,
                       TtlsParameter)

logger = logging.getLogger(__name__)

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
    remaining_seconds = int((expiration_time - datetime.now()).total_seconds())
    return config.replace("$ssid", ssid).replace("$cert_name", cert_name,)\
        .replace("$cert_content", cert_format_content).replace("$cert_pass", cert_pass)\
        .replace("$remaining_seconds", str(remaining_seconds))


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

    def __init__(self, db_conf_dict, pki_conf_dict):
        self.host = db_conf_dict["host"]
        self.user = db_conf_dict["user"]
        self.passwd = db_conf_dict["passwd"]
        self.db = db_conf_dict["db"]
        self.client_certs_dir = pki_conf_dict["client_certs_dir"]
        self.ca_crt = crypto.load_certificate(
            crypto.FILETYPE_PEM, open(pki_conf_dict["ca_crt"]).read())
        self.ca_key = crypto.load_privatekey(
            crypto.FILETYPE_PEM, open(pki_conf_dict["ca_key"]).read(), "waacs")
        self.C = pki_conf_dict["country"]
        self.ST = pki_conf_dict["state"]
        self.O = pki_conf_dict["organization"]
        et = pki_conf_dict["encryption_type"]
        if et == "RSA":
            self.encryption_type = crypto.TYPE_RSA
        elif et == "DSA":
            self.encryption_type = crypto.TYPE_DSA
        else:
            logger.warning("encryption type is not set")
        self.key_size = int(pki_conf_dict["key_size"])
        self.expiration_timespan = int(pki_conf_dict["expiration_timespan"])

    def on_get(self, req, resp, token):
        logger.debug("request wifiauth by token: {}".format(token))
        if "iPhone" in req.user_agent or "iPad" in req.user_agent:
            device_type = "iOS"
        elif "Android" in req.user_agent:
            device_type = "Android"
        else:
            resp.status = falcon.HTTP_401
            resp.body = "This system is iPhone and Android only"
            return
        logger.debug("accessed device type is {}".format(device_type))
        with db.connect(**self.db_conn_args) as cur:
            rownum = cur.execute(
                "SELECT access_issuer_id, token_activation_time, association_ssid FROM token \
                 WHERE token = %s", (token, ))
            if not rownum:
                logger.warning("not found token: %s", token)
                resp.status = falcon.HTTP_401
                resp.body = "Error: invalid token (deleted or unregistered)"
                return
            access_issuer_id, token_activation_time, association_ssid = cur.fetchone()
            logger.debug("token {} is activated by {} at {}".format(
                token, access_issuer_id, token_activation_time))
            # TODO because debug
            if False:
                # if now - token_issuance_time > timedelta(seconds=60):
                logger.warning("expiration token: %s", token)
                resp.status = falcon.HTTP_401
                resp.body = "Error: expiration token"
                return
            logger.debug("token is valid")
            cur.execute("DELETE FROM token WHERE token = %s", (token, ))
            eap_type = "EAP-TLS" if device_type == "iOS" else "EAP_TTLS"
            user_id, password, serial = self.gen_credential(cur, access_issuer_id, eap_type)
            p12, expiration_time = self.gen_certificate(serial, user_id)
            cert_subject = p12.get_certificate().get_subject().get_components()
            logger.debug("certificate {} expiration_time {}".format(cert_subject, expiration_time))
            p12_export = p12.export(password)
            cur.execute("INSERT INTO certificate(id, cert_filename) VALUES(%s, %s)",
                        (str(serial), os.path.join(self.client_certs_dir, user_id + ".p12")))
            logger.debug("create credential user_id: %s password: %s", user_id, password)
            if device_type == "iOS":
                resp.content_type = MIMETYPE_MOBILECONFIG
                config = make_mobileconfig_tls(
                    association_ssid, user_id, p12_export, password, expiration_time)
                resp.body = config
            elif device_type == "Android":
                resp.content_type = MIMETYPE_WAACSCONFIG
                config = make_waacsconfig_ttls(association_ssid, user_id, password)
                resp.body = config

    def gen_credential(self, cur, access_issuer_id, eap_type):
        now = datetime.now()
        while True:
            user_id = "".join([random.choice(api.SOURCE_CHAR) for x in range(32)])
            cur.execute("SELECT TRUE FROM user WHERE user_id = %s", (user_id, ))
            if not cur.fetchone():
                break
        password = "".join([random.choice(api.SOURCE_CHAR)
                            for x in range(32)])
        cur.execute("INSERT INTO user(user_id, password, issuance_time, access_issuer_id, eap_type) \
                     VALUES(%s, %s, %s, %s, %s)",
                    (user_id, password, api.format_time(now), access_issuer_id, eap_type))
        cur.execute("SELECT LAST_INSERT_ID() FROM user")
        serial = cur.fetchone()[0]
        return user_id, password, serial

    def gen_certificate(self, serial, user_id):
        key = crypto.PKey()
        key.generate_key(self.encryption_type, self.key_size)
        crt = crypto.X509()
        sbj = crt.get_subject()
        sbj.C = self.C
        sbj.ST = self.ST
        sbj.O = self.O
        sbj.CN = user_id
        crt.gmtime_adj_notBefore(0)
        crt.gmtime_adj_notAfter(self.expiration_timespan)
        exp_time_utc = datetime.strptime(crt.get_notAfter(), "%Y%m%d%H%M%SZ")
        tz = timezone("Asia/Tokyo")
        exp_time_jst = tz.fromutc(exp_time_utc).astimezone(tz).replace(tzinfo=None)
        crt.set_serial_number(serial)
        crt.set_issuer(self.ca_crt.get_subject())
        crt.set_pubkey(key)
        crt.sign(self.ca_key, "sha256")
        p12 = crypto.PKCS12()
        p12.set_privatekey(key)
        p12.set_certificate(crt)
        p12.set_ca_certificates([self.ca_crt])
        return p12, exp_time_jst
