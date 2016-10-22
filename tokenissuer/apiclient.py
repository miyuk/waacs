# -*- coding: utf-8 -*-

import sys
import requests
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
                logger.error("API request error: %s (%s)", url, r.status_code)
                raise requests.RequestException()
            data = json.loads(r.text)
            return (data["token"], data["issuance_time"])
        except:
            logger.error("error: %s", sys.exc_info())
            return (None, None)

    def requestwifi_url(self, token):
        return "https://{0}:{1}/request_wifi/{2}/".format(self.server_address, self.server_port, token)
