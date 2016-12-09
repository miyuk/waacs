# -*- coding: utf-8 -*-

import json
import logging
import sys

import requests
from requests import RequestException

logger = logging.getLogger(__name__)


class ApiClient(object):

    TYPE_NFC = "NFC"
    TYPE_QR = "QR"

    @property
    def credential(self):
        return {"issuer_id": self.issuer_id, "issuer_password": self.issuer_password}

    def __init__(self, api_conf_dict):
        self.server_address = api_conf_dict["server_address"]
        self.server_port = api_conf_dict["server_port"]
        self.issuer_id = api_conf_dict["issuer_id"]
        self.issuer_password = api_conf_dict["issuer_password"]

    def issue_token(self, access_type):
        try:
            url = "https://{0}:{1}/issue_token/".format(
                self.server_address, self.server_port)
            data = self.credential
            data.update({"issuer_id": self.issuer_id,
                         "access_type": access_type})
            logger.debug("send issue_token request to %s", url)
            r = requests.post(url, json.dumps(data))
            if r.status_code != requests.codes.ok:
                raise RequestException(
                    "API request error: {} ({})".format(url, r.status_code))
            data = json.loads(r.text)
            return (data["token"], data["issuance_time"])
        except Exception as e:
            logger.error(e.message)
            raise sys.exc_info()

    def requestwifi_url(self, ssid, token):
        return "https://{0}:{1}/request_wifi_auth/{2}/{3}/".format(self.server_address,
                                                                   self.server_port,
                                                                   ssid, token)
