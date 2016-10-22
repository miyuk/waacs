# -*- coding: utf-8 -*-

from threading import Thread
from nfc import ContactlessFrontend
from nfc.ndef import Record, UriRecord, Message
import logging
logger = logging.getLogger(__name__)
from tokenissuer.apiclient import ApiClient
import nfcclient


class NfcIssuer(Thread):

    def __init__(self, server_address, server_port, issuer_id, issuer_password):
        super(NfcIssuer, self).__init__()
        self.api_client = ApiClient(server_address, server_port, issuer_id, issuer_password)
        self.daemon = True

    def run(self):
        while True:
            with ContactlessFrontend("usb") as clf:
                llc = clf.connect(llcp={"on-connect": (lambda llc: False)})
                if not llc:
                    logger.error("NFC connection failure")
                    return
                logger.debug("LLCP link is successfully established\n%s", llc)
                client = nfcclient.NfcClient(llc)
                th = Thread(target=llc.run)
                th.daemon = True
                th.start()
                token, issuance_time = self.api_client.issue_token()
                params = {"token": token, "issuance_time": issuance_time}
                client.send_waacs_message(params)
                looger.debug("LLCP link is closing")
                self.llc_thread.join()
                logger.debug("LLCP link is closed")
