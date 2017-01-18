# -*- coding: utf-8 -*-

import logging
from threading import Event, Thread
from time import sleep

from RPi import GPIO
from tokenissuer import ApiClient

logger = logging.getLogger(__name__)


class QrIssuer(Thread):

    def __init__(self, api_client, qr_conf_dict):
        super(QrIssuer, self).__init__()
        self.api_client = api_client
        self.update_inteval = int(qr_conf_dict["update_interval"])
        self.sensor_port = int(qr_conf_dict["sensor_port"])
        self.stop_event = Event()

    def run(self):
        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BOARD)
        GPIO.setup(self.sensor_port, GPIO.IN)
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
                while True:
                    if self.stop_event.is_set():
                        return
                    elif not self.is_sensing():
                        break
                    sleep(0.1)
                self.activate_token(ApiClient.TYPE_QR)
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

    def stop(self):
        logger.debug("process is stopping")
        self.stop_event.set()
