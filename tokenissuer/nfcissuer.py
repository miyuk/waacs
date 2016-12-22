# -*- coding: utf-8 -*-

import logging
from threading import Event, Thread
from time import sleep, time

from nfc import ContactlessFrontend

import nfcclient
from tokenissuer import ApiClient

logger = logging.getLogger(__name__)


class NfcIssuer(Thread):

    def __init__(self, ssid, api_conf_dict):
        super(NfcIssuer, self).__init__()
        self.api_client = ApiClient(api_conf_dict)
        self.ssid = ssid
        self.stop_event = Event()
        self.next_token, issuance_time = self.api_client.issue_token(ApiClient.TYPE_NFC)

    def run(self):
        while not self.stop_event.is_set():
            try:
                with ContactlessFrontend("usb") as clf:
                    logger.info("touch NFC device: %s", clf)
                    started = time()

                    def terminate_check():
                        span = time() - started
                        return span > 30 or self.stop_event.is_set()
                    llc = clf.connect(llcp={"on-connect": (lambda llc: False)},
                                      terminate=terminate_check)
                    if not llc:
                        logger.warning("NFC connection timeout and continue...")
                        continue
                    logger.debug("LLCP link is successfully established\n%s", llc)
                    token = self.next_token
                    self.api_client.activate_token(token)
                    self.next_token = None
                    client = nfcclient.NfcClient(llc)
                    th = Thread(target=llc.run)
                    th.daemon = True
                    th.start()
                    url = self.api_client.requestwifi_url(self.ssid, token)
                    client.send_waacs_message(url)
                    logger.debug("LLCP link is closing")
                    th.join()
                    logger.debug("LLCP link is closed")
                self.next_token, issuance_time = self.api_client.issue_token(ApiClient.TYPE_NFC)
                logger.debug("get token: %s", self.next_token)
            except Exception as e:
                logger.exception(e)
                sleep(1)
        logger.info("process is stopped")

    def stop(self):
        logger.debug("process is stopping")
        self.stop_event.set()
