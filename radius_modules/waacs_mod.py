#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os
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
    # timestamp = timestamp.strftime("%Y-%m-%d %H:%M:%S")
    ap_id = get_attribute(p, "NAS-Identifier")
    try:
        with MySQLdb.connect(host=HOST, db=DB, user=USER, passwd=PASSWD) as cursor:
            # パスワードチェック→有効期限チェック→同時接続数チェック→認証
            sql = "SELECT password, issuance_time, authentication_time, expiration_time FROM {0} WHERE user_id = '{1}'".format(
                USER_TBL, user_id)
            line_num = cursor.execute(sql)
            # 登録されていなければReject
            if line_num is 0L:
                radlog(L_AUTH, "not found user: {0}".format(user_id))
                return RLM_MODULE_REJECT
            result = cursor.fetchone()
            # パスワードが間違っていればReject
            if(result[0] != password):
                radlog(L_AUTH, "mismatch password for user: {0}".format(user_id))
                return RLM_MODULE_REJECT
            # すでに認証済み
            if authentication_time is not None:
                # 有効期限切れならReject
                if expiration_time > timestamp:
                    radlog(L_AUTH, "expired user")
                    return RLM_MODULE_REJECT
            else:
                # タッチから5秒以上経過でReject
                if result[1] > issuance_time + timedelta(seconds=5):
                    radlog(L_AUTH, "waacs authentication timeout")
                    return RLM_MODULE_REJECT
                auth_time = timestamp.strftime("%Y-%m-%d %H:%M:%S")
                exp_time = datetime(datetime + timedelta(hours=8)).strftime("%Y-%m-%d %H:%M:%S")
                sql = "UPDATE {0} SET authentication_time = '{1}', expiration_time = '{2}'".format(
                    USER_TBL, auth_time, exp_time)
                cursor.execute(sql)

            sql = "SELECT mac_address FROM {0} WHERE user_id = '{1}'".format(DEVICE_TBL, user_id)
            line_num = cursor.execute(sql)
            # 台数制限でReject
            if line_num >= 3L:
                radlog(L_AUTH, "limit of the deveices number")
                return RLM_MODULE_REJECT
            sql = "INSERT INTO {0} (user_id, mac_address, first_access_time, first_access_ap)\
                  VALUES ('{1}', '{2}', '{3}', '{4}')".format(user_id, mac_addr, timestamp.strftime(), ap_id)
            cursor.execute(Sql)
    except Exception as e:
        radlog(L_ERR, str(e))
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
