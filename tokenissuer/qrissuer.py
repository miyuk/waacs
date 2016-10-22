# -*- coding: utf-8 -*-

from threading import Thread
import time
from nfc import ContactlessFrontend
from nfc.ndef import Record, UriRecord, Message
import logging
logger = logging.getLogger(__name__)
import qrcode
from tokenissuer.apiclient import ApiClient


class QrIssuer(Thread):

    def __init__(self, server_address, server_port, issuer_id, issuer_password,
                 qr_output_path, update_inteval=30):
        super(QrIssuer, self).__init__()
        self.api_client = ApiClient(server_address, server_port, issuer_id, issuer_password)
        self.qr_output_path = qr_output_path
        self.update_inteval = update_inteval
        self.daemon = True

    def run(self):
        while True:
            token, issuance_time = self.api_client.issue_token()
            qr_img = qrcode.make(self.api_client.requestwifi_url(token))
            qr_img.save(self.qr_output_path)
            time.sleep(self.update_inteval)
