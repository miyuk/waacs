# -*- coding: utf-8 -*-

import json
import datetime
import logging
import base64
import api
logger = logging.getLogger(__name__)

TYPE_TLS = "EAP-TLS"
TYPE_TTLS = "EAP-TTLS"


class Parameter:
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
        dct[self.SSID] = self.ssid
        dct[self.EAP_TYPE] = self.eap_type
        if self.eap_type == TYPE_TLS:
            dct[self.TLS_PARAMETER] = self.tls_parameter.to_dict()
        elif self.eap_type == TYPE_TTLS:
            dct[self.TTLS_PARAMETER] = self.ttls_parameter.to_dict()
        if self.issuance_time:
            dct[self.ISSUANCE_TIME] = api.format_time(self.issuance_time)
        if self.expiration_time:
            dct[self.EXPIRATION_TIME] = api.format_time(self.expiration_time)
        return dct

    @classmethod
    def parse(cls, dct):
        param = Parameter()
        param.ssid = dct[cls.SSID]
        param.eap_type = dct[cls.EAP_TYPE]
        if param.eap_type == TYPE_TLS:
            param.tls_parameter = TlsParameter.parse(dct[cls.TLS_PARAMETER])
        elif param.eap_type == TYPE_TTLS:
            param.ttls_parameter = TtlsParameter.parse(dct[cls.TTLS_PARAMETER])
        if ISSUANCE_TIME in dct:
            param.issuance_time = api.parse_time(dct[cls.ISSUANCE_TIME])
        if EXPIRATION_TIME in dct:
            param.expiration_time = api.parse_time(dct[cls.EXPIRATION_TIME])
        return param


class TlsParameter:
    CLIENT_CERTIFICATE_NAME = "clientCertificateName"
    CLIENT_CERTIFICATE_CONTENT = "clientCertificateContent"
    PASSPHRASE = "passphrase"

    def __init__(self):
        self.client_certificate_name = None
        self.client_certificate_content = None
        self.passphrase = None

    def to_dict(self):
        dct = {}
        dct[self.CLIENT_CERTIFICATE_NAME] = self.client_certificate_name
        dct[self.CLIENT_CERTIFICATE_CONTENT] = base64.standard_b64encode(
            self.client_certificate_content)
        dct[self.PASSPHRASE] = self.passphrase
        return dct
# TODO
    # @classmethod
    # def parse(cls):
    #     tls = TlsParameter()
    #     self.client_certificate_name = dct[cls.CLIENT_CERTIFICATE_NAME]
    #     self.client_certificate_content = base64.standard_b64decode(
    #         dct[cls.CLIENT_CERTIFICATE_CONTENT])
    #     self.passphrase = dct[cls.PASSPHRASE]
    #     return parameter


class TtlsParameter:
    USER_ID = "userId"
    PASSWORD = "password"

    def __init__(self):
        self.user_id = None
        self.password = None

    def to_dict(self):
        dct = {}
        dct[self.USER_ID] = self.user_id
        dct[self.PASSWORD] = self.password
        return dct

    @classmethod
    def parse(cls, dct):
        parameter = Parameter()
        parameter.user_id = dct[cls.USER_ID]
        parameter.password = dct[cls.PASSWORD]
        return parameter
