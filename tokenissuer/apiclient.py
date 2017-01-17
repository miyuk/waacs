# -*- coding: utf-8 -*-

import json
import logging
import random

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

    def issue_token(self, access_type):
        try:
            url = "https://{0}:{1}/issue_token/".format(
                self.server_address, self.server_port)
            data = self.credential
            data.update({"issuer_id": self.issuer_id,
                         "access_type": access_type,
                         "association_ssid": self.ssid})
            logger.debug("send issue_token request to %s", url)
            r = requests.post(url, json.dumps(data))
            if r.status_code != requests.codes.ok:
                raise RequestException("API request error: {} ({})".format(url, r.status_code))
            data = json.loads(r.text)
            token = data["token"]
            token_issuance_time = data["token_issuance_time"]
            return (token, token_issuance_time)
        except Exception as e:
            logger.exception(e.message)
            return (None, None)

    def activate_token(self, token):
        try:

            url = "https://{0}:{1}/activate_token/".format(self.server_address, self.server_port)
            data = self.credential
            conn_num = "".join([random.choice("0123456789") for _ in range(5)])
            data.update({"issuer_id": self.issuer_id, "token": token,
                         "connection_number": conn_num})
            logger.debug("send token activation request to %s", url)
            r = requests.post(url, json.dumps(data))
            if r.status_code != requests.codes.ok:
                raise RequestException("API request error: {} ({})".format(url, r.status_code))
            data = json.loads(r.text)
            activation_time = data["token_activation_time"]
            return activation_time, conn_num
        except Exception as e:
            logger.exception(e.message)
            return (None, None)

    def request_wifi_url(self, token):
        return "https://{0}:{1}/request_wifi_auth/{2}/".format(
            self.server_address, self.server_port, token)
