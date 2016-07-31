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
# 呼び出しは1回のみでNFCデバイスをロックする
# プログラム終了後にロックが解除される


class NfcConnection(object):
    WAACS_MESSAGE_RECORD_TYPE = "urn:nfc:ext:waacs:msg"

    def __init__(self):
        self.server = None
        self.client = None
        self.is_connected = False
        self.llc_thread = False
        self.clf = nfc.ContactlessFrontend("usb")

    def connect(self):
        if self.is_connected:
            self.close()
        logger.debug("NFC connecting")
        result = self.clf.connect(llcp={"on-startup": self.on_startup,
                                        "on-connect": self.on_connect})
        if result is False:
            logger.error("NFC connection failure")
            return False
        return True

    def on_startup(self, llc):
        self.client = nfcclient.NfcClient(llc)
        self.server = nfcserver.NfcServer(llc)
        return llc

    # on_connectでｔｈｒｅａｄブロックして処理しない
    def on_connect(self, llc):
        logger.debug("LLCP Link is successfully established by {0}".format(str(llc)))
        self.is_connected = True
        self.llc_thread = threading.Thread(target=llc.run)
        self.llc_thread.daemon = True
        self.llc_thread.start()
        return False

    def close(self):
        if not self.is_connected:
            return
        if not self.client is None:
            self.client.close()
            self.client = None
            self.server = None
        self.is_connected = False
        self.llc_thread.join()
        logger.info("NFC connection is closed")

    def get_payload(self, ndef_message):
        payload = ""
        for record in ndef_message:
            payload += record.data
        return payload

    def send_waacs_message(self, json_text):
        record = nfc.ndef.Record(
            record_type=self.WAACS_MESSAGE_RECORD_TYPE, data=json_text)
        message = nfc.ndef.Message(record)
        self.client.send(message)
