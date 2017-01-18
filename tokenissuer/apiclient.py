# -*- coding: utf-8 -*-

import json
import logging
import random
import sqlite3

import requests
from requests import RequestException

logger = logging.getLogger(__name__)


class ApiClient(object):

    TYPE_NFC = "NFC"
    TYPE_QR = "QR"

    @property
    def credential(self):
        return {"issuer_id": self.issuer_id, "issuer_password": self.issuer_password}

    def __init__(self, api_conf_dict, wifi_conf_dict):
        self.server_address = api_conf_dict["server_address"]
        self.server_port = api_conf_dict["server_port"]
        self.issuer_id = api_conf_dict["issuer_id"]
        self.issuer_password = api_conf_dict["issuer_password"]
        self.ssid = wifi_conf_dict["ssid"]
        self.token_db_file = api_conf_dict["token_db_file"]
        self.next_token = None
        self.issue_token()

    def generate_token(self, access_type):
        self.activate_token(access_type)

    def issue_token(self):
        if self.next_token:
            return
        try:
            url = "https://{0}:{1}/issue_token/".format(self.server_address, self.server_port)
            data = self.credential
            data.update({"issuer_id": self.issuer_id, "association_ssid": self.ssid})
            logger.debug("send issue_token request to %s", url)
            r = requests.post(url, json.dumps(data))
            if r.status_code != requests.codes.ok:
                raise RequestException("API request error: {} ({})".format(url, r.status_code))
            data = json.loads(r.text)
            token = data["token"]
            issuance_time = data["token_issuance_time"]
            with sqlite3.connect(self.token_db_file) as cur:
                cur.execute("INSERT INTO token(token, issuance_time) VALUES(?, ?)",
                            (token, issuance_time))
            self.next_token = token
            return token
        except Exception as e:
            logger.exception(e.message)
            raise e

    def activate_token(self, access_type):
        if not self.next_token:
            return
        token = self.next_token
        self.next_token = None
        logger.debug("activting token: %s", token)

        try:
            url = "https://{0}:{1}/activate_token/".format(self.server_address, self.server_port)
            data = self.credential
            conn_num = "".join([random.choice("0123456789") for _ in range(5)])
            data.update({"issuer_id": self.issuer_id, "token": token,
                         "access_type": access_type,
                         "connection_number": conn_num})
            logger.debug("send token activation request to %s", url)
            r = requests.post(url, json.dumps(data))
            if r.status_code != requests.codes.ok:
                raise RequestException("API request error: {} ({})".format(url, r.status_code))
            data = json.loads(r.text)
            activation_time = data["token_activation_time"]
            with sqlite3.connect(self.token_db_file) as cur:
                cur.execute("UPDATE token SET activation_time = ?, connection_number = ?, \
                             access_type = ? WHERE token = ?",
                            (activation_time, conn_num, access_type, token))
            return token
        except Exception as e:
            logger.exception(e.message)
            raise e

    def request_wifi_url(self, token):
        return "https://{0}:{1}/request_wifi_auth/{2}/".format(
            self.server_address, self.server_port, token)
