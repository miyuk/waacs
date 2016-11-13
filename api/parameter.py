# -*- coding: utf-8 -*-

import json
import datetime
import logging
logger = logging.getLogger(__name__)
import base64
import api

class Parameter:
    TYPE_TLS = "EAP-TLS"
    TYPE_TTLS = "EAP-TTLS"

    SSID = "ssid"
    EAP_TYPE = "eapType"
    TLS_PARAMETER = "tlsParameter"
    TTLS_PARAMETER = "ttlsParameter"
    ISSUANCE_TIME = "issuanceTime"
    EXPIRATION_TIME = "expirationTime"

    def __init__(self):
        self.ssid = None
        self.eap_type = None
        self.tls_parameter = None
        self.ttls_parameter = None
        self.issuance_time = None
        self.expiration_time = None

    def to_dict(self):
        dct = {}
        dct[SSID] = self.ssid
        dct[EAP_TYPE] = self.eap_type
        if self.eap_type == TYPE_TLS:
            dct[TLS_PARAMETER] = self.tls_parameter.to_dict()
        elif self.eap_type == TYPE_TTLS:
            dct[TTLS_PARAMETER] = self.ttls_parameter.to_dict()
        if self.issuance_time:
            dct[ISSUANCE_TIME] = api.format_time(self.issuance_time)
        if self.expiration_time:
            dct[EXPIRATION_TIME] = api.format_time(self.expiration_time)
        return dct

    @staticmethod
    def parse(dct):
        param = Parameter()
        param.ssid = dct[SSID]
        param.eap_type = dct[EAP_TYPE]
        if param.eap_type == TYPE_TLS:
            param.tls_parameter = TlsParameter.parse(dct[TLS_PARAMETER])
        elif param.eap_type == TYPE_TTLS:
            param.ttls_parameter = TtlsParameter.parse(dct[TTLS_PARAMETER])
        if ISSUANCE_TIME in dct:
            param.issuance_time = api.parse_time(dct[ISSUANCE_TIME])
        if EXPIRATION_TIME in dct:
            param.expiration_time = api.parse_time(dct[EXPIRATION_TIME])
        return param


class TlsParameter:
    CLIENT_CERTIFICATE_FILENAME = "clientCertificateFilename"
    CLIENT_CERTIFICATE_CONTENT = "clientCertificateContent"
    PASSPHRASE = "passphrase"

    def __init__(self):
        self.client_certificate_filename = None
        self.client_certificate_content = None
        self.passphrase = None

    def to_dict(self):
        dct = {}
        dct[CLIENT_CERTIFICATE_FILENAME] = self.client_certificate_filename
        dct[CLIENT_CERTIFICATE_CONTENT] = base64.standard_b64encode(self.client_certificate_content)
        dct[PASSPHRASE] = self.passphrase
        return dct

    @staticmethod
    def parse(dct):
        tls = TlsParameter()
        self.client_certificate_filename = dct[CLIENT_CERTIFICATE_FILENAME]
        self.client_certificate_content = base64.standard_b64decode(
            dct[CLIENT_CERTIFICATE_CONTENT])
        self.passphrase = dct[PASSPHRASE]
        return parameter


class TtlsParameter:
    USER_ID = "userId"
    PASSWORD = "password"

    def __init__(self):
        self.user_id = None
        self.password = None

    def to_dict(self):
        dct = {}
        dct[USER_ID] = self.user_id
        dct[PASSWORD] = self.password
        return dct

    @staticmethod
    def parse(dct):
        parameter = Parameter()
        parameter.user_id = dct[USER_ID]
        parameter.password = dct[PASSWORD]
        return parameter
