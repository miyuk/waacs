# -*- coding: utf-8 -*-
import nfc
import nfc.snep
import logging
logger = logging.getLogger(__name__)
class NfcClient(nfc.snep.SnepClient):
    def __init__(self, llc):
        nfc.snep.client.SnepClient.__init__(self, llc)
        self.is_sent = False
    def send(self, ndef_message):
        return self._send(ndef_message)
    def _send(self, ndef_message):
        if(not self.put(ndef_message)):
            logger.error("client can't send message")
            return False
        self.is_sent = True
        return True
