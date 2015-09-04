# -*- coding: utf-8 -*-
import threading
import nfc
import nfc.clf
import nfc.llcp
import nfc.ndef
import nfc.snep
import datetime
import nfcclient
import nfcserver
import logging
logger = logging.getLogger(__name__)

class NfcConnection(object):
    WAACS_MESSAGE_RECORD_TYPE = "urn:nfc:ext:waacs:msg"

    def __init__(self):
        self.server = None
        self.client = None
        self.is_connected = False
        self.clf = nfc.ContactlessFrontend("usb")

    def connect(self):
        if self.is_connected:
            logger.warn("already connected to NFC")
            return False
        logger.debug("connecting NFC")
        llc = self.clf.connect(llcp={"on-connect":self.on_connect})
        if llc is None:
            logger.error("can't connect NFC")
            return False
        self.client = nfcclient.NfcClient(llc)
        self.server = nfcserver.NfcServer(llc)
        return True

    def on_connect(self, llc):
        logger.debug("connected NFC")
        self.is_connected = True
        th = threading.Thread(target=llc.run)
        th.daemon = True
        th.start()
        return False

    def close(self):
        if not self.is_connected:
            logger.warn("not connected to NFC")
            return
        self.client.close()
        self.is_connected = False
        logger.info("closed NFC connection")

    def get_payload(self, ndef_message):
        payload = ""
        for record in ndef_message:
            payload += record.data
        return payload

    def send_waacs_message(self, json_text):
       record = nfc.ndef.Record(record_type=self.WAACS_MESSAGE_RECORD_TYPE, data=json_text)
       message = nfc.ndef.Message(record)
       self.client.send(message)
