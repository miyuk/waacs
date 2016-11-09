# -*- coding: utf-8 -*-

import sys
from threading import Thread, Event
from nfc import ContactlessFrontend
from nfc.ndef import Record, UriRecord, Message
from time import time
import logging
logger = logging.getLogger(__name__)
import traceback
from tokenissuer.apiclient import ApiClient
import nfcclient


class NfcIssuer(Thread):

    def __init__(self, server_address, server_port, issuer_id, issuer_password):
        super(NfcIssuer, self).__init__()
        self.api_client = ApiClient(server_address, server_port, issuer_id, issuer_password)
        self.stop_event = Event()

    def run(self):
        while not self.stop_event.is_set():
            try:
                with ContactlessFrontend("usb") as clf:
                    token, issuance_time = self.api_client.issue_token()
                    started = time()
                    def terminate_check():
                        span = time() - started
                        return span > 5 or self.stop_event.is_set()
                    llc = clf.connect(llcp={"on-connect": (lambda llc: False)},
                                      terminate=terminate_check)
                    if not llc:
                        logger.warning("NFC connection timeout and continue...")
                        continue
                    logger.debug("LLCP link is successfully established\n%s", llc)
                    client = nfcclient.NfcClient(llc)
                    th = Thread(target=llc.run)
                    th.daemon = True
                    th.start()
                    params = {"token": token, "issuance_time": issuance_time}
                    client.send_waacs_message(params)
                    logger.debug("LLCP link is closing")
                    th.join()
                    logger.debug("LLCP link is closed")
            except:
                logger.error("error: %s", traceback.format_exc())
        logger.info("process is stopped")

    def stop(self):
        logger.debug("process is stopping")
        self.stop_event.set()
