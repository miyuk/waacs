#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os
import MySQLdb
import radiusd
from datetime import datetime

HOST = "localhost"
USER = "waacs"
PASSWD = "waacs"
DB = "waacs"
USER_TBL = "user"
DEVICE_TBL = "user_device"
ISSUER_TBL = "issuer"


def authorize(p):
    radiusd.radlog(radiusd.L_INFO, "*** python authorize ***")
    radiusd.radlog(radiusd.L_INFO, str(p))
    return radiusd.RLM_MODULE_OK


def authenticate(p):
    radiusd.radlog(radiusd.L_INFO, "*** python authenticate ***")
    radiusd.radlog(radiusd.L_INFO, str(p))
    user_id = get_attribute(p, "User-Name")
    password = get_attribute(p, "User-Password")
    mac_addr = get_attribute(p, "Calling-Station-Id")
    timestamp = get_attribute(p, "Event-Timestamp")
    timestamp = " ".join(timestamp.split(" ")[:-1])  # タイムゾーン部分を削除
    timestamp = datetime.strptime(timestamp, "%b %d $Y %H:%M:%S").strftime("%Y-%m-%d %H:%M:%S")
    ap_id = get_attribute(p, "NAS-Identifier")

    with MySQLdb.connect(host=HOST, db=DB, user=USER, passwd=PASSWD) as cursor:
        sql = "SELECT password FROM {0} WHERE user_id = '{1}'".format(USER_TBL, user_id)
        cursor.execute(sql)
        result = cursor.fetchall()[0][0]
        # 登録されていなければReject
        if(result != password):
            return radiusd.RLM_MODULE_REJECT
        sql = "SELECT mac_address FROM {0} WHERE user_id = '{1}'".format(DEVICE_TBL, user_id)
        cursor.execute(sql)
        result = cursor.fetchall()
        # 指定台数以上がすでに接続済みでReject
        if result is not None & & len(result) >= 3:
            return radiusd.RLM_MODULE_REJECT
        # 3台以内なら
        sql = "INSERT INTO {0} (user_id, mac_address, first_access_time, first_access_ap)\
              VALUES ('{1}', '{2}', '{3}', '{4}')".format(user_id, password, timestamp, ap_id)
        return radiusd.RLM_MODULE_OK


def post_auth(p):
    radiusd.radlog(radiusd.L_INFO, "*** python post_auth ***")
    radiusd.radlog(radiusd.L_INFO, str(p))
    return radiusd.RLM_MODULE_OK


def get_attribute(p, attr_name):
    for attr in p:
        if attr[0] == attr_name:
            return attr[1].strip('"')
    # if attr_name is nothing
    return ""
