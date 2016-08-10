# -*- coding: utf-8 -*-
import MySQLdb
import random
from datetime import datetime, timedelta
import logging
logger = logging.getLogger(__name__)
import waacs


class UserDB(object):
    DB = "waacs"
    USER_TBL = "user"
    DEVICE_TBL = "user_device"
    ISSUER_TBL = "issuer"
    SOURCE_CHAR = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
    DEFAULT_EXPIRATION = timedelta(hours=8)

    # コンストラクタ
    def __init__(self, host, user, passwd):
        self.db_host = host
        self.db_user = user
        self.db_passwd = passwd

    # SQL実行
    def _execute(self, sql):
        logger.debug("execute sql: " + sql)
        with MySQLdb.connect(host=self.db_host,
                             db=self.DB,
                             user=self.db_user,
                             passwd=self.db_passwd) as cursor:
            cursor.execute(sql)
            result = cursor.fetchall()
            cursor.close()
        return result

    def create_user(self):
        # 重複がなくなるまでランダム作成
        while True:
            # 10文字のユーザ名とパスワードの生成
            user_id = "".join([random.choice(self.SOURCE_CHAR)
                               for x in xrange(10)])
            if not self.exists_user(user_id):
                break
        password = "".join([random.choice(self.SOURCE_CHAR)
                            for x in xrange(10)])
        logger.debug("create user: %s : %s", user_id, password)
        return (user_id, password)
    # userテーブルにuser_idが存在するかチェック

    def exists_user(self, user_id):
        sql = "SELECT COUNT(*) FROM {0} WHERE user_id = '{1}'".format(
            self.USER_TBL, user_id)
        count = self._execute(sql)[0][0]
        return count != 0
    # userテーブルに登録

    def issue_user(self, user_id, password, issuer_id):
        # ユーザ登録
        now = datetime.now()
        issuance_time = waacs.format_time(now)
        expiration_time = waacs.format_time(
            now + self.DEFAULT_EXPIRATION)
        sql = "INSERT INTO {0} (user_id, password, access_issuer_id, issuance_time, expiration_time) VALUES('{1}', '{2}', '{3}', '{4}', '{5}')".format(
            self.USER_TBL, user_id, password, issuer_id, issuance_time, expiration_time)
        self._execute(sql)
        logger.info("issue user: %s", user_id)
        return (now, now + self.DEFAULT_EXPIRATION)

    def check_issuer(self, issuer_id, password):
        sql = "SELECT password FROM {0} WHERE issuer_id = '{1}'".format(
            self.ISSUER_TBL, issuer_id)
        result = self._execute(sql)
        if len(result) == 0:
            logger.warn("can't find issuer_id: %s", issuer_id)
            return False
        elif password != result[0][0]:
            logger.warn("%s's password is wrong", issuer_id)
            return False
        else:
            return True
