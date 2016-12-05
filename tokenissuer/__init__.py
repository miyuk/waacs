# -*- coding: utf-8 -*-

import logging
from tokenissuer.apiclient import ApiClient
from tokenissuer.nfcissuer import NfcIssuer
from tokenissuer.qrissuer import QrIssuer
logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())
logger.setLevel(logging.INFO)
