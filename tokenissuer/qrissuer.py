# -*- coding: utf-8 -*-

import logging
import sqlite3
from threading import Event, Thread
from time import sleep

from RPi import GPIO
from tokenissuer import ApiClient

logger = logging.getLogger(__name__)


class QrIssuer(Thread):

    def __init__(self, api_client, qr_conf_dict):
        super(QrIssuer, self).__init__()
        self.api_client = api_client
        self.token_db_file = qr_conf_dict["token_db_file"]
        self.update_inteval = int(qr_conf_dict["update_interval"])
        self.sensor_port = int(qr_conf_dict["sensor_port"])
        self.stop_event = Event()

    def run(self):
        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BOARD)
        GPIO.setup(self.sensor_port, GPIO.IN)
        self.issue_token()
        try:
            while not self.stop_event.is_set():
                logger.debug("distance sensor is waiting for device...")
                while True:
                    if self.stop_event.is_set():
                        return
                    elif self.is_sensing():
                        break
                    sleep(0.1)
                logger.debug("distance sensor detects a device")
                logger.debug("activting token: %s", self.next_token)
                token = self.next_token
                self.activate_token(token)
                self.next_token = None
                while True:
                    if self.stop_event.is_set():
                        return
                    elif not self.is_sensing():
                        break
                    sleep(0.1)
                self.issue_token()
                logger.info("waiting update interval: %f seconds", self.update_inteval)
                self.stop_event.wait(self.update_inteval)
        except Exception as e:
            logger.exception(e)
        finally:
            GPIO.cleanup()
            logger.info("process is stopped")

    def is_sensing(self):
        try:
            value = GPIO.input(self.sensor_port)
            return bool(value)
        except Exception as e:
            logger.exception(e)

    def issue_token(self):
        token, issuance_time = self.api_client.issue_token(ApiClient.TYPE_QR)
        if not token or not issuance_time:
            raise Exception("cannnot issue token")
        logger.debug("get token: %s at %s", token, issuance_time)
        with sqlite3.connect(self.token_db_file) as cur:
            cur.execute("INSERT INTO token(token, issuance_time) VALUES(?, ?)",
                        (token, issuance_time))
        self.next_token = token

    def activate_token(self, token):
        activation_time = self.api_client.activate_token(token)
        if not activation_time:
            raise Exception("cannot activate token")
        logger.debug("activation time is %s", activation_time)
        with sqlite3.connect(self.token_db_file) as cur:
            cur.execute("UPDATE token SET activation_time = ? WHERE token = ?",
                        (activation_time, token))

    def stop(self):
        logger.debug("process is stopping")
        self.stop_event.set()
