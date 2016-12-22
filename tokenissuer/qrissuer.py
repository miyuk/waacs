# -*- coding: utf-8 -*-

import logging
import sqlite3
import traceback
from threading import Event, Thread
from time import sleep

from RPi import GPIO
from tokenissuer import ApiClient

logger = logging.getLogger(__name__)


class QrIssuer(Thread):

    def __init__(self, ssid, api_conf_dict, qr_conf_dict):
        super(QrIssuer, self).__init__()
        self.ssid = ssid
        self.api_client = ApiClient(api_conf_dict)
        self.token_db_file = qr_conf_dict["token_db_file"]
        self.update_inteval = int(qr_conf_dict["update_interval"])
        self.sensor_port = int(qr_conf_dict["sensor_port"])
        self.stop_event = Event()
        self.next_token, issuance_time = self.api_client.issue_token(ApiClient.TYPE_QR)

    def run(self):
        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BOARD)
        GPIO.setup(self.sensor_port, GPIO.IN)
        while not self.stop_event.is_set():
            try:
                logger.debug("waiting for closing a device")
                while not self.stop_event.is_set():
                    if not self.is_sensing():
                        break
                    sleep(0.1)
                logger.debug("detected a device")
                logger.debug("activting token: %s", self.next_token)
                token = self.next_token
                activation_time = self.api_client.activate_token(token)
                self.next_token = None
                with sqlite3.connect(self.token_db_file) as cur:
                    cur.execute("UPDATE token SET activation_time = ? WHERE token = ?",
                                (activation_time, token))
                while not self.stop_event.is_set():
                    if self.is_sensing():
                        break
                    sleep(0.1)
                self.next_token, issuance_time = self.api_client.issue_token(ApiClient.TYPE_QR)
                logger.debug("get token %s", token)
                cur.execute("INSERT INTO token(token, issuance_time) VALUES(?, ?)",
                            (token, issuance_time))

            except:
                logger.exception("error: %s", traceback.format_exc())
            finally:
                self.stop_event.wait(self.update_inteval)
        logger.info("process is stopped")

    def is_sensing(self):
        try:
            value = GPIO.input(self.sensor_port)
            return bool(value)
        except Exception as e:
            logger.warning(e.message)

    def stop(self):
        logger.debug("process is stopping")
        GPIO.cleanup()
        self.stop_event.set()
