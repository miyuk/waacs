#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os
import re
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
AUTH_TIMEOUT = timedelta(seconds=5)
TIME_FORMAT = "%Y-%m-%d %H:%M:%S"


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
    mac_addr = format_mac_addr(mac_addr)
    timestamp = get_attribute(p, "Event-Timestamp")
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
            if auth_time is None:
                # タッチから5秒以上経過でReject
                if timestamp > issuance_time + AUTH_TIMEOUT:
                    radlog(L_AUTH, "waacs authentication timeout")
                    return RLM_MODULE_REJECT
                auth_time = timestamp.strftime(TIME_FORMAT)
                exp_time = (timestamp + timedelta(hours=8)).strftime(TIME_FORMAT)
                sql = "UPDATE {0} SET authentication_time = '{1}', expiration_time = '{2}' WHERE user_id = '{3}'".format(
                    USER_TBL, auth_time, exp_time, user_id)
                cursor.execute(sql)
            else:
                # 有効期限切れならReject
                if timestamp > exp_time:
                    radlog(L_AUTH, "expired user: {0}".format(user_id))
                    return RLM_MODULE_REJECT
            # 接続機器チェック
            sql = "SELECT mac_address FROM {0} WHERE user_id = '{1}'".format(DEVICE_TBL, user_id)
            line_num = cursor.execute(sql)
            connected_mac_addrs = [v[0] for v in cursor.fetchall()]
            has_auth = mac_addr in connected_mac_addrs
            # 台数制限でReject
            if not has_auth and line_num >= 3L:
                radlog(L_AUTH, "limit of deveices")
                return RLM_MODULE_REJECT
            elif not has_auth:
                radlog(L_INFO, "first access device")
                sql = "INSERT INTO {0} (user_id, mac_address, first_access_time, first_access_ap)\
                    VALUES ('{1}', '{2}', '{3}', '{4}')".format(
                    DEVICE_TBL, user_id, mac_addr, timestamp.strftime(TIME_FORMAT), ap_id)
                cursor.execute(sql)
            else:
                radlog(L_INFO, "{0} has been already connected".format(mac_addr))
            return RLM_MODULE_OK
    except Exception as e:
        radlog(L_ERR, "error: {0}".format(str(e)))
        for line in traceback.format_exc().split("\n"):
            radlog(L_ERR, line)
        return RLM_MODULE_REJECT


def format_mac_addr(mac):
    mac = re.sub("[^0-9a-fA-F]", "", mac)
    mac = [mac[i:i + 2] for i in range(0, 12, 2)]
    return "{0}-{1}-{2}-{3}-{4}-{5}".format(*mac)


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
