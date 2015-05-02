# -*- coding: utf-8 -*-
import sys
import nfcmanager
import usermanager
import negotiation
import datetime
import logging
import threading
import time
import nfc
class Waacs(object):
    
    #コンストラクタ
    def __init__(self, ssid, host, db, user, passwd):
        self.stop_event = threading.Event()
        self.nfc_interrupt_event = threading.Event()
        self.ssid = ssid
        self.user_manager = usermanager.UserManager(host, db, user, passwd)
        self.nfc_manager = nfcmanager.NfcManager(self.on_receive_cb)
        self.user_manager_thread = threading.Thread(target=self.user_manager_run)
        self.user_manager_thread.setDaemon(True)
        self.nfc_manager_thread = threading.Thread(target=self.nfc_manager_run)
        self.nfc_manager_thread.setDaemon(True)
    def user_manager_run(self):
        while not self.stop_event.is_set():
            logging.info("user_manager_run(): Start")
            self.user_manager.update_user_mac_address()
            self.user_manager.delete_expired_user()
            time.sleep(self._DEL_USER_INTERVAL)

