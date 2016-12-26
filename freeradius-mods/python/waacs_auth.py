#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
import traceback
from datetime import datetime, timedelta

import MySQLdb as db

from config import (DB, EXPIRATION_TIMESPAN, FIRST_ACCESS_TIMEOUT, HOST,
                    MAX_DEVICES, PASSWD, USER)
from radiusd import (L_AUTH, L_DBG, L_ERR, L_INFO, L_PROXY, RLM_MODULE_FAIL,
                     RLM_MODULE_HANDLED, RLM_MODULE_INVALID, RLM_MODULE_NOOP,
                     RLM_MODULE_NOTFOUND, RLM_MODULE_NUMCODES, RLM_MODULE_OK,
                     RLM_MODULE_REJECT, RLM_MODULE_UPDATED,
                     RLM_MODULE_USERLOCK, radlog)

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
    mac_addr = format_mac_addr(get_attribute(p, "Calling-Station-Id"))
    tsstr = " ".join(get_attribute(p, "Event-Timestamp").split(" ")[:-1])  # タイムゾーン部分を削除
    timestamp = datetime.strptime(tsstr, "%b %d %Y %H:%M:%S")
    ap_id = get_attribute(p, "NAS-Identifier")
    try:
        with db.connect(host=HOST, db=DB, user=USER, passwd=PASSWD) as cur:
            # パスワードチェック→有効期限チェック→同時接続数チェック→認証
            line_num = cur.execute("SELECT password, issuance_time, authentication_time, \
                                    access_issuer_id, eap_type \
                                    FROM user WHERE user_id = %s", (user_id, ))
            # 登録されていなければReject
            if not line_num:
                radlog(L_AUTH, "not found user: {0}".format(user_id))
                return RLM_MODULE_REJECT
            true_pass, issu_time, auth_time, issu_id, eap_type = cur.fetchone()
            # パスワードが間違っていればReject
            if(password != true_pass):
                radlog(L_AUTH, "mismatch password for user: {0}".format(user_id))
                return RLM_MODULE_REJECT
            if not auth_time:
                # 認証情報発行から初回接続まで指定秒以上経過でReject
                if timestamp > issu_time + timedelta(seconds=FIRST_ACCESS_TIMEOUT):
                    radlog(L_AUTH, "first access timeout")
                    return RLM_MODULE_REJECT
                # TODO post_authに移動させる
                cur.execute("UPDATE user SET authentication_time = %s WHERE user_id = %s",
                            (timestamp.strftime(TIME_FORMAT), user_id))
            # 有効時間はconfigで設定
            expr_time = auth_time + timedelta(seconds=EXPIRATION_TIMESPAN)
            # 有効期限切れならReject
            if timestamp > expr_time:
                radlog(L_AUTH, "expired authentication user: {0}".format(user_id))
                return RLM_MODULE_REJECT
            # 接続機器チェック
            cur.execute("SELECT mac_address FROM user_device WHERE user_id = %s", (user_id, ))
            connected_mac_addrs = [v[0] for v in cur.fetchall()]
            if not (mac_addr in connected_mac_addrs):
                # 台数制限でReject
                if len(connected_mac_addrs) >= MAX_DEVICES:
                    radlog(L_AUTH, "limit of deveices")
                    return RLM_MODULE_REJECT
                radlog(L_INFO, "first access device")
                cur.execute("INSERT INTO user_device (user_id, mac_address, first_access_time, first_access_ap) \
                    VALUES (%s, %s, %s, %s)",
                            (user_id, mac_addr, timestamp.strftime(TIME_FORMAT), ap_id))
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
    if len(mac) != 6:
        return None
    return "{0}-{1}-{2}-{3}-{4}-{5}".format(*mac)


def post_auth(p):
    radlog(L_INFO, "*** python post_auth ***")
    radlog(L_INFO, str(p))
    return RLM_MODULE_NOOP


def get_attribute(p, attr_name):
    for attr in p:
        if attr[0] == attr_name:
            return attr[1].strip('"')
    # if attr_name is nothing
    return ""
