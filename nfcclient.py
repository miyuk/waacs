# -*- coding: utf-8 -*-
import nfc
import nfc.snep
import threading
class NfcClient(nfc.snep.client.SnepClient):
    def __init__(self, llc):
        nfc.snep.client.SnepClient.__init__(self, llc)
        self.is_sent = False
    def send(self, ndef_message):
        threading.Thread(target=self._send, args=(ndef_message,)).start()
    def _send(self, ndef_message):
        if(not self.put(ndef_message)):
            logging.error("client can't send message")
        self.is_sent = True