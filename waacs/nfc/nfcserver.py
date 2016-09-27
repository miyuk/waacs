# -*- coding: utf-8 -*-
from nfc.snep import SnepServer
import logging
logger = logging.getLogger(__name__)


class NfcServer(SnepServer):

    def __init__(self, llc):
        SnepServer.__init__(self, llc)
        self.is_received = False

    def put(self, ndef_message):
        return ndef_message
