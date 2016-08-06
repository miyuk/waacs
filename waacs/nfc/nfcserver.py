# -*- coding: utf-8 -*-
import nfc
import nfc.snep
import logging
logger = logging.getLogger(__name__)


class NfcServer(nfc.snep.SnepServer):

    def __init__(self, llc):
        nfc.snep.server.SnepServer.__init__(self, llc)
        self.is_received = False

    def put(self, ndef_message):
        return ndef_message
