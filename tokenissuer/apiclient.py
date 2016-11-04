# -*- coding: utf-8 -*-

import sys
import requests
from requests import RequestException
import json
import logging
logger = logging.getLogger(__name__)


class ApiClient(object):

    @property
    def credential(self):
        return {"issuer_id": self.issuer_id, "issuer_password": self.issuer_password}

    def __init__(self, server_address, server_port, issuer_id, issuer_password):
        self.server_address = server_address
        self.server_port = server_port
        self.issuer_id = issuer_id
        self.issuer_password = issuer_password

    def issue_token(self):
        try:
            url = "https://{0}:{1}/issue_token/".format(self.server_address, self.server_port)
            r = requests.post(url, json.dumps(self.credential))
            if r.status_code != requests.codes.ok:
                raise RequestException("API request error: {} ({})".format(url, r.status_code))
            data = json.loads(r.text)
            return (data["token"], data["issuance_time"])
        except:
            raise sys.exc_info()

    def requestwifi_url(self, ssid, token):
        return "https://{0}:{1}/request_wifi_auth/{2}/{3}/".format(self.server_address,
                                                                   self.server_port,
                                                                   ssid, token)
