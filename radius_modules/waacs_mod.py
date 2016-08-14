#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os
import traceback
import MySQLdb
from radiusd import *
from datetime import datetime, timedelta

HOST = "localhost"
USER = "waacs"
PASSWD = "waacs"
DB = "waacs"
USER_TBL = "user"
DEVICE_TBL = "user_device"
ISSUER_TBL = "issuer"


def authorize(p):
    radlog(L_INFO, "*** python authorize ***")
    radlog(L_INFO, str(p))
    return RLM_MODULE_OK


def authenticate(p):
    radlog(L_INFO, "*** python authenticate ***")
    radlog(L_INFO, str(p))
    user_id = get_attribute(p, "User-Name")
    password = get_attribute(p, "User-Password")
    mac_addr = get_attribute(p, "Calling-Station-Id")
    timestamp = get_attribute(p, "Event-Timestamp")
    radlog(L_INFO, timestamp)
    timestamp = " ".join(timestamp.split(" ")[:-1])  # タイムゾーン部分を削除
    timestamp = datetime.strptime(timestamp, "%b %d %Y %H:%M:%S")
    ap_id = get_attribute(p, "NAS-Identifier")
    try:
        with MySQLdb.connect(host=HOST, db=DB, user=USER, passwd=PASSWD) as cursor:
            # パスワードチェック→有効期限チェック→同時接続数チェック→認証
            sql = "SELECT password, issuance_time, authentication_time, expiration_time FROM {0} WHERE user_id = '{1}'".format(
                USER_TBL, user_id)
            line_num = cursor.execute(sql)
            # 登録されていなければReject
            if line_num == 0L:
                radlog(L_AUTH, "not found user: {0}".format(user_id))
                return RLM_MODULE_REJECT
            result = cursor.fetchone()
            # パスワードが間違っていればReject
            if(result[0] != password):
                radlog(L_AUTH, "mismatch password for user: {0}".format(user_id))
                return RLM_MODULE_REJECT
            issuance_time, auth_time, exp_time = result[1:]
            # すでに認証済み
            if auth_time is not None:
                # 有効期限切れならReject
                if exp_time > timestamp:
                    radlog(L_AUTH, "expired user: {0}".format(user_id))
                    return RLM_MODULE_REJECT
            else:
                # タッチから5秒以上経過でReject
                if timestamp > issuance_time + timedelta(seconds=5):
                    radlog(L_AUTH, "waacs authentication timeout")
                    return RLM_MODULE_REJECT
                auth_time = timestamp.strftime("%Y-%m-%d %H:%M:%S")
                exp_time = (timestamp + timedelta(hours=8)).strftime("%Y-%m-%d %H:%M:%S")
                sql = "UPDATE {0} SET authentication_time = '{1}', expiration_time = '{2}' WHERE user_id = '{3}'".format(
                    USER_TBL, auth_time, exp_time, user_id)
                cursor.execute(sql)
            # 接続機器チェック
            sql = "SELECT mac_address FROM {0} WHERE user_id = '{1}'".format(DEVICE_TBL, user_id)
            line_num = cursor.execute(sql)
            # 台数制限でReject
            if line_num >= 3L:
                radlog(L_AUTH, "limit of the deveices")
                return RLM_MODULE_REJECT
            result = cursor.fetchall()
            if line_num > 0:
                radlog(L_INFO, "already connected devices are {0}".format(
                    ", ".join([v[0] for v in result])))
            else:
                radlog(L_INFO, "first access")
            for row in result:
                if mac_addr == row[0]:
                    radlog(L_INFO, "already connected mac address: {0}".format(mac_addr))
                    return RLM_MODULE_OK
            sql = "INSERT INTO {0} (user_id, mac_address, first_access_time, first_access_ap)\
                VALUES ('{1}', '{2}', '{3}', '{4}')".format(
                DEVICE_TBL, user_id, mac_addr, timestamp.strftime("%Y-%m-%d %H:%M:%S"), ap_id)
            cursor.execute(sql)
    except Exception as e:
        for line in traceback.format_exc().split("\n"):
            radlog(L_ERR, line)
        return RLM_MODULE_REJECT
    return RLM_MODULE_OK


def post_auth(p):
    radlog(L_INFO, "*** python post_auth ***")
    radlog(L_INFO, str(p))
    return RLM_MODULE_OK


def get_attribute(p, attr_name):
    for attr in p:
        if attr[0] == attr_name:
            return attr[1].strip('"')
    # if attr_name is nothing
    return ""
