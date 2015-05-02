# -*- coding: utf-8 -*-
import threading
import nfc
import nfc.clf
import nfc.llcp
import nfc.ndef
import nfc.snep
import datetime
import logging
import nfcclient
import nfcserver


class NfcConnection(object):
    #aar_message = nfc.ndef.Message(nfc.ndef.Record(record_type=_AAR_RECORD_TYPE, data=_APP_PKG_NAME))
    def __init__(self):
        self.server = None
        self.client = None
        self.connect_begin_time = None
        #self.timeout = timeout
        #self.on_receive_cb = on_receive_cb
        self.clf = nfc.ContactlessFrontend("usb")
    def connect(self, on_connect_cb):
        #self.connect_begin_time = datetime.datetime.now()
        self.clf.connect(llcp={
            "on-startup":self.startup,
            "on-connect":on_connect_cb})
        #self.connect_begin_time = None
    #サーバとクライアントを初期化
    def startup(self, clf, llc):
        logging.debug("on_startup_cb(): Start")
        self.server = NfcServer(llc)
        self.client = NfcClient(llc)
        self.server.start()
        return llc
    #def check_timeout(self):
    #    if(self.interrupt_event.is_set()):
    #        return True
    #    #if(self.nfc_manager.snep_start_time + self._OFFER_TIMEOUT < datetime.datetime.now()):
    #    #    logging.debug("timeout")
    #    #    return True
    #    else:
    #        return False
    #NDEFメッセージをテキストに変換
    #def get_payload(self, ndef_message):
    #    payload = ""
    #    for record in ndef_message:
    #        text_record = nfc.ndef.TextRecord(record)
    #        payload += text_record.text
    #    return payload
    def get_payload(self, ndef_message):
        payload = ""
        for record in ndef_message:
            payload = record.data
        return payload
    #def send_text_message(self, text):
    #    ndef_message = nfc.ndef.TextRecord(text=text)
    #    ndef_message = nfc.ndef.Message(ndef_message)
    #    self.client.send(ndef_message)
    #def send_waacs_message(self, json_text):
    #    ndef_message = nfc.ndef.Record(record_type=self._MESSAGE_RECORD_TYPE, data=json_text)
    #    ndef_message = nfc.ndef.Message(ndef_message)
    #    self.client.send(ndef_message)