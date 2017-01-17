# -*- coding: utf-8 -*-

import logging
from threading import Event, Thread

from nfc import ContactlessFrontend

import nfcclient
from tokenissuer import ApiClient

logger = logging.getLogger(__name__)


class NfcIssuer(Thread):

    def __init__(self, api_client):
        super(NfcIssuer, self).__init__()
        self.api_client = api_client
        self.stop_event = Event()

    def run(self):
        self.next_token, issuance_time = self.api_client.issue_token(ApiClient.TYPE_NFC)
        try:
            while not self.stop_event.is_set():
                with ContactlessFrontend("usb") as clf:
                    logger.info("touch NFC device: %s", clf)

                    def terminate_check():
                        return self.stop_event.is_set()
                    llc = clf.connect(llcp={"on-connect": (lambda llc: False)},
                                      terminate=terminate_check)
                    if not llc:
                        logger.warning("LLCP link is not established. retry...")
                        continue
                    logger.debug("LLCP link is successfully established\n%s", llc)
                    client = nfcclient.NfcClient(llc)
                    th = Thread(target=llc.run)
                    th.daemon = True
                    th.start()
                    token = self.next_token
                    url = self.api_client.request_wifi_url(token)
                    logger.debug("send waacs message")
                    client.send_waacs_message(url)
                    logger.debug("activating token: %s", token)
                    activation_time, conn_num = self.api_client.activate_token(token)
                    logger.debug("activation time is %s", activation_time)
                    self.next_token = None
                    logger.debug("LLCP link is closing")
                    th.join()
                    logger.debug("LLCP link is closed")
                self.next_token, issuance_time = self.api_client.issue_token(ApiClient.TYPE_NFC)
                logger.debug("get token: %s at %s", self.next_token, issuance_time)
        except Exception as e:
            logger.exception(e)
        finally:
            logger.info("process is stopped")

    def stop(self):
        logger.debug("process is stopping")
        self.stop_event.set()
