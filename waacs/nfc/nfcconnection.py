# -*- coding: utf-8 -*-
from threading import Thread
from nfc import ContactlessFrontend
from nfc.ndef import Record, UriRecord, Message
import logging
logger = logging.getLogger(__name__)
import nfcclient
import nfcserver

WAACS_MESSAGE_RECORD_TYPE = "urn:nfc:ext:waacs:msg"
ANDROID_APPKLICATION_RECORD_TYPE = "urn:nfc:ext:android.com:pkg"


# 呼び出しは1回のみでNFCデバイスをロックする
# プログラム終了後にロックが解除される
class NfcConnection(object):

    def __init__(self):
        self.server = None
        self.client = None
        self.is_connected = False
        self.llc_thread = False
        self.clf = ContactlessFrontend("usb")

    def connect(self):
        if self.is_connected:
            self.close()
        logger.debug("NFC listen")
        llc = self.clf.connect(llcp={"on-connect": (lambda llc: False)})
        if llc is False:
            logger.error("NFC connection failure")
            return False
        logger.debug("LLCP link is successfully established\n {0}".format(str(llc)))
        self.is_connected = True
        self.client = nfcclient.NfcClient(llc)
        self.server = nfcserver.NfcServer(llc)
        self.llc_thread = Thread(target=llc.run)
        self.llc_thread.daemon = True
        self.llc_thread.start()
        return True

    def close(self):
        if not self.is_connected:
            return
        logger.debug("NFC connection is closing")
        if not self.client is None:
            self.client.close()
            self.client = None
            self.server = None
        self.is_connected = False
        self.llc_thread.join()
        logger.info("NFC connection is closed")

    def send_waacs_message(self, json_text, android_package_name):
        record = Record(record_type=WAACS_MESSAGE_RECORD_TYPE, data=json_text)
        aar = self.create_aar(android_package_name)
        message = Message((record,) + aar)
        self.client.send(message)

    def create_aar(self, android_package_name):
        uri = "https://play.google.com/store/apps/details?id={0}&feature=beam".format(
            android_package_name)
        record1 = UriRecord(uri)
        record2 = Record(
            record_type=ANDROID_APPKLICATION_RECORD_TYPE, data=android_package_name)
        return (record1, record2)
