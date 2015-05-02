# -*- coding: utf-8 -*-
import json
import datetime
import logging
def time_tostring(time):
    return datetime.datetime.strftime(time, _TIME_FORMAT)

def parse_tstr(tstr):
    return datetime.datetime.strptime(tstr, _TIME_FORMAT)

class Parameter:
    def __init__(self):
        self.message_type = None
        self.ssid = None
        self.user_id = None
        self.password = None
        self.mail_address = None
        self.regist_time = None
        self.expire_time = None
        self.mac_address = None
        self.required_info = None
    def to_json(self):
        json_dict = dict()
        if(self.message_type is not None):
            json_dict[Attribute.MESSAGE_TYPE] = self.message_type
        if(self.ssid is not None):
            json_dict[Attribute.SSID] = self.ssid
        if(self.user_id is not None):
            json_dict[Attribute.USER_ID] = self.user_id
        if(self.password is not None):
            json_dict[Attribute.PASSWORD] = self.password
        if(self.mail_address is not None):
            json_dict[Attribute.MAIL_ADDRESS] = self.mail_address
        if(self.mac_address is not None):
            json_dict[Attribute.MAC_ADDRESS] = self.mac_address
        if(self.regist_time is not None):
            tstr = time_tostring(self.regist_time)
            json_dict[Attribute.REGIST_TIME] = tstr
        if(self.expire_time is not None):
            tstr = time_tostring(self.expire_time)
            json_dict[cls.Attribute.EXPIRE_TIME] = tstr
        json_text = json.dumps(json_dict)
        return json_text

    @staticmethod
    def make_from_json(json_text):
        parameter = Parameter()
        json_dict = json.loads(json_text)
        if(json_dict.has_key(Attribute.MESSAGE_TYPE)):
            parameter.message_type = json_dict[Attribute.MESSAGE_TYPE]
        if(json_dict.has_key(Attribute.USER_ID)):
            parameter.user_id = json_dict[Attribute.USER_ID]
        if(json_dict.has_key(Attribute.PASSWORD)):
            parameter.password = json_dict[Attribute.PASSWORD]
        if(json_dict.has_key(Attribute.MAIL_ADDRESS)):
            parameter.mail_address = json_dict[Attribute.MAIL_ADDRESS]
        if(json_dict.has_key(Attribute.REGIST_TIME)):
            tstr = json_dict[Attribute.REGIST_TIME]
            parameter.regist_time = parse_tstr(tstr)
        if(json_dict.has_key(Attribute.EXPIRE_TIME)):
            tstr = json_dict[Attribute.EXPIRE_TIME]
            parameter.expire_time = parse_tstr(tstr)
        if(json_dict.has_key(Attribute.MAC_ADDRESS)):
            parameter.mac_address = json_dict[Attribute.MAC_ADDRESS]
        if(json_dict.has_key(Attribute.REQUIRED_INFO)):
            parameter.required_info = json_dict[Attribute.REQUIRED_INFO]
        return parameter
    
class MessageType:
    OFFER = "OFFER"
    ACCEPT = "ACCEPT"
    DECLINE = "DECLINE"
    EXTEND = "EXTEND"
class Attribute:
    MESSAGE_TYPE = "MessageType"
    SSID = "Ssid"
    USER_ID = "UserId"
    PASSWORD = "Password"
    REGIST_TIME = "RegistTime"
    EXPIRE_TIME = "ExpireTime"
    MAIL_ADDRESS = "MailAddress"
    MAC_ADDRESS = "MacAddress"
    REQUIRED_INFO = "RequiredInfo"
