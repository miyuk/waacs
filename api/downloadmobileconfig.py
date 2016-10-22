# -*- coding: utf-8 -*-

import logging
logger = logging.getLogger(__name__)

templete_file_path = "./templete.mobileconfig"


def make_mobileconfig(ssid, user_id, password):
    config = open(templete_file_path).read()
    return config.replace("$ssid", ssid).replace("$userId", user_id).replace("$password", password)


class DownloadMobleconfigApi(object):

    def on_get(self, req, resp, ssid, user_id, password):
        resp.content_type = "application/x-apple-aspen-config"
        config = make_mobileconfig(ssid, user_id, password)
        resp.body = config
