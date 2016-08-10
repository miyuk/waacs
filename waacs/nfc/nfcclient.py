# -*- coding: utf-8 -*-
from nfc.snep import SnepClient
import logging
logger = logging.getLogger(__name__)


class NfcClient(SnepClient):

    def __init__(self, llc):
        SnepClient.__init__(self, llc)
        self.is_sent = False

    def send(self, ndef_message):
        if(not self.put(ndef_message)):
            logger.error("client can't send message")
            return False
        self.is_sent = True
        return True
