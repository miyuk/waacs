# -*- coding: utf-8 -*-

import sys
from threading import Thread, Event
import time
from nfc import ContactlessFrontend
from nfc.ndef import Record, UriRecord, Message
import logging
logger = logging.getLogger(__name__)
import qrcode
from tokenissuer.apiclient import ApiClient


class QrIssuer(Thread):

    def __init__(self, ssid, server_address, server_port, issuer_id, issuer_password,
                 qr_output_path, update_inteval=30):
        super(QrIssuer, self).__init__()
        self.ssid = ssid
        self.api_client = ApiClient(server_address, server_port, issuer_id, issuer_password)
        self.qr_output_path = qr_output_path
        self.update_inteval = update_inteval
        self.stop_event = Event()

    def run(self):
        while not self.stop_event.is_set():
            try:
                token, issuance_time = self.api_client.issue_token()
                qr_img = qrcode.make(self.api_client.requestwifi_url(ssid, token))
                qr_img.save(self.qr_output_path)
            except:
                logger.error("error: %s", sys.exc_info())
            finally:
                self.stop_event.wait(self.update_inteval)
        logger.info("process is stopped")

    def stop(self):
        logger.debug("process is stopping")
        self.stop_event.set()
