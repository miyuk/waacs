# -*- coding: utf-8 -*-
import json
import datetime
import logging
logger = logging.getLogger(__name__)
import stringutils


class Parameter:

    def __init__(self):
        self.ssid = None
        self.user_id = None
        self.password = None
        self.issuance_time = None
        self.expiration_time = None

    def to_json(self):
        json_dict = dict()
        if self.ssid is not None:
            json_dict[Attribute.SSID] = self.ssid
        if self.user_id is not None:
            json_dict[Attribute.USER_ID] = self.user_id
        if self.password is not None:
            json_dict[Attribute.PASSWORD] = self.password
        if self.issuance_time is not None:
            tstr = stringutils.format_time(self.issuance_time)
            json_dict[Attribute.ISSUANCE_TIME] = tstr
        if self.expiration_time is not None:
            tstr = stringutils.format_time(self.expiration_time)
            json_dict[Attribute.EXPIRATION_TIME] = tstr
        json_text = json.dumps(json_dict)
        return json_text

    @staticmethod
    def parse(json_text):
        parameter = Parameter()
        json_dict = json.loads(json_text)
        if json_dict.has_key(Attribute.USER_ID):
            parameter.user_id = json_dict[Attribute.USER_ID]
        if json_dict.has_key(Attribute.PASSWORD):
            parameter.password = json_dict[Attribute.PASSWORD]
        if json_dict.has_key(Attribute.ISSUANCE_TIME):
            tstr = json_dict[Attribute.ISSUANCE_TIME]
            parameter.ISSUANCE_TIME = stringutils.parse_time(tstr)
        if json_dict.has_key(Attribute.EXPIRATION_TIME):
            tstr = json_dict[Attribute.EXPIRATION_TIME]
            parameter.EXPIRATION_TIME = stringutils.parse_time(tstr)
        return parameter


class Attribute:
    SSID = "ssid"
    USER_ID = "userId"
    PASSWORD = "password"
    ISSUANCE_TIME = "issuanceTime"
    EXPIRATION_TIME = "expirationTime"
