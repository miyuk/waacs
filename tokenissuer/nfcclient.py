# -*- coding: utf-8 -*-

import logging
import json
from nfc.snep import SnepClient
from nfc.ndef import Record, Message, UriRecord
logger = logging.getLogger(__name__)

WAACS_MESSAGE_RECORD_TYPE = "urn:nfc:ext:waacs:msg"
ANDROID_APPKLICATION_RECORD_TYPE = "urn:nfc:ext:android.com:pkg"
ANDROID_PACKAGE_NAME = "jp.ac.oit.elc.mail.waacsandroidclient"


class NfcClient(SnepClient):

    @property
    def waacs_aars(self):
        uri = "https://play.google.com/store/apps/details?id={0}&feature=beam".format(
            ANDROID_PACKAGE_NAME)
        r1 = UriRecord(uri)
        r2 = Record(record_type=ANDROID_APPKLICATION_RECORD_TYPE,
                    data=ANDROID_PACKAGE_NAME)
        return (r1, r2)

    def __init__(self, llc):
        super(NfcClient, self).__init__(llc)
        self.is_sent = False

    def send(self, ndef_message):
        if(not self.put(ndef_message)):
            logger.error("client can't send message: %s", ndef_message)
            return False
        self.is_sent = True
        return True

    def send_waacs_message(self, url):
        record = Record(record_type=WAACS_MESSAGE_RECORD_TYPE)
        record.data = url
        message = Message((record,) + self.waacs_aars)
        logger.debug("sending message: %s", message.pretty())
        self.send(message)
        logger.debug("sent message")
