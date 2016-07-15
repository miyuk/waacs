#!/usr/bin/env python
# -*- coding: utf-8 -*-

import radiusd
import MySQLdb


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
    user_id = get_attribute(p, "User-Name").strip('"')
    password = get_attribute(p, "User-Password").strip('"')
    sql = "SELECT password FROM {0} WHERE user_id = '{1}'".format(USER_TBL, user_id)
    result = execute_sql(sql)[0][0]
    if(result != password):
        return radiusd.RLM_MODULE_REJECT

    return radiusd.RLM_MODULE_OK


def post_auth(p):
    radiusd.radlog(radiusd.L_INFO, "*** python post_auth ***")
    radiusd.radlog(radiusd.L_INFO, str(p))
    user_id = get_attribute(p, "User-Name").strip('"')
    password = get_attribute(p, "User-Password").strip('"')
    sql = "INSERT"
    return radiusd.RLM_MODULE_OK


# backend
def execute_sql(sql):
    with MySQLdb.connect(host=HOST, user=USER, passwd=PASSWD, db=DB) as cursor:
        cursor.execute(sql)
        return cursor.fetchall()


def get_attribute(p, attr_name):
    for attr in p:
        if attr[0] == attr_name:
            return attr[1]
    # if attr_name is nothing
    return ""
