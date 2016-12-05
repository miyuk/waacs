# -*- coding: utf-8 -*-

import logging
from api.issuetoken import IssueTokenApi
from api.requestwifiauth import RequestWifiAuthApi
from api.parameter import Parameter, TlsParameter, TtlsParameter
logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())
logger.setLevel(logging.INFO)


HOST = "localhost"
USER = "waacs"
PASSWD = "waacs"
DB = "waacs"
USER_TBL = "user"
DEVICE_TBL = "user_device"
ISSUER_TBL = "issuer"
SOURCE_CHAR = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
TIME_FORMAT = "%Y-%m-%d %H:%M:%S"


def format_time(time):
    return datetime.datetime.strftime(time, TIME_FORMAT)


def parse_time(tstr):
    return datetime.datetime.strptime(tstr, TIME_FORMAT)
