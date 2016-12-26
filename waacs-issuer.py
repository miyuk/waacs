#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import os
import sys
import time
from ConfigParser import SafeConfigParser
from logging.config import fileConfig

from tokenissuer import ApiClient, NfcIssuer, QrIssuer

logger = logging.getLogger(__name__)


fileConfig(os.path.join(sys.path[0], "config/issuer_log.cfg"))
config = SafeConfigParser()
config.read(os.path.join(sys.path[0], "config/issuer.cfg"))
qr_conf_dict = dict(config.items("QrIssuer"))
wifi_conf_dict = dict(config.items("WifiInfo"))
api_conf_dict = dict(config.items("ApiClient"))


def main(argv):
    api_client = ApiClient(api_conf_dict, wifi_conf_dict)
    nfc_issuer = NfcIssuer(api_client)
    nfc_issuer.start()
    qr_issuer = QrIssuer(api_client, qr_conf_dict)
    qr_issuer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logger.warning("exit by KeyboardInterrupt")
        sys.exit(0)
    finally:
        nfc_issuer.stop()
        qr_issuer.stop()


if __name__ == '__main__':
    main(sys.argv)
