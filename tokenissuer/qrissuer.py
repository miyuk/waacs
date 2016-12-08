# -*- coding: utf-8 -*-

import logging
import sqlite3
import sys
import time
import traceback
from threading import Event, Thread

import qrcode
from nfc import ContactlessFrontend
from nfc.ndef import Message, Record, UriRecord

from tokenissuer import ApiClient

logger = logging.getLogger(__name__)


class QrIssuer(Thread):

    def __init__(self, ssid, api_conf_dict, qr_output_path, update_inteval=30):
        super(QrIssuer, self).__init__()
        self.ssid = ssid
        self.api_client = ApiClient(api_conf_dict)
        self.qr_output_path = qr_output_path
        self.update_inteval = update_inteval
        self.stop_event = Event()

    def run(self):
        while not self.stop_event.is_set():
            try:
                token, issuance_time = self.api_client.issue_token(
                    self.api_client.TYPE_QR)
                with sqlite3.connect(self.qr_output_path) as cur:
                    cur.execute("INSERT INTO token(token, issuance_time) \
                        VALUES(%s, %s)", (token, issuance_time))
                # qr_img = qrcode.make(
                #     self.api_client.requestwifi_url(self.ssid, token))
                # qr_img.save(self.qr_output_path)
            except:
                logger.error("error: %s", traceback.format_exc())
            finally:
                self.stop_event.wait(self.update_inteval)
        logger.info("process is stopped")

    def stop(self):
        logger.debug("process is stopping")
        self.stop_event.set()
