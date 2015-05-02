# -*- coding: utf-8 -*-
import nfc
import nfc.snep

class NfcServer(nfc.snep.server.SnepServer):
    def __init__(self, llc):
        nfc.snep.server.SnepServer.__init__(self, llc)
        self.is_received = False
        #self.on_receive_cb = on_receive_cb
    def put(self, ndef_message):
        self._receive(ndef_message)
        return nfc.snep.Success
    def receive(self, ndef_message):
        if(self.receive_callback is not None):
            #self.on_receive_cb(ndef_message)
            self.is_received = True