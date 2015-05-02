# -*- coding: utf-8 -*-
import json
import MySQLdb
import random
import datetime
import logging
import threading
import parameter
import datetime

class UserDB(object):
    user_table = "waacs.user"
    check_table = "radius.radcheck"
    account_table = "radius.radacct"
    __source_char = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"

    _SELECT_RECENTLY_ACCESS_USERS_SQL = "SELECT username, callingstationid FROM radacct WHERE (acctstarttime > NOW() - INTERVAL 5 MINUTE) GROUP BY username;"
    #コンストラクタ
    def __init__(self, host, user, passwd):
        self.host = host
        #self.db = db
        self.user = user
        self.passwd = passwd
        self.lock = threading.Lock()
    #del_expired_userの停止
    def stop(self):
        self.stop_event.set()
    #プライベートメソッド
    #SQL実行
    def _execute(self, sql):
        logging.debug("_execute sql: " + sql)
        with self.lock:
            with MySQLdb._connect(host=self.host,
                db=self.db,
                user=self.user,
                passwd=self.passwd) as cursor:
                    cursor._execute(sql)
                    result = cursor.fetchall()
                    cursor.close()
        return result
    #MySQLサーバへの接続処理
    def _connect(self):
        _connector = MySQLdb._connect(host=self.host, 
            #db=self.db, 
            user=self.user, 
            passwd=self.passwd)
        return _connector
    #サーバから切断処理
    def _disconnect(self, _connector):
        _connector.cursor().close()
        _connector.close()
    #MySQL標準処理関数
    def _select_records(self, table, field="*", relation=None, filter=None, using=None, group=None):
        sql = "SELECT {field} FROM {table}".format(field=field, table=table)
        if relation is not None:
            sql += " JOIN {relation}".format(relation=relation)
        if using is not None:
            sql += " USING ('{using}')".format(using=using)
        if filter is not None:
            sql += " WHERE {filter}".format(filter=filter)
        if group is not None:
            sql += " GROUP BY {group}".format(group=group)
        records = self._execute(sql)
        return table
    def _delete_records(self, table, filter):
        sql ="DELETE FROM {table} WHERE {filter}".format(table=table, filter=filter)
        count = self._execute(sql)
        return count
    def _insert_record(self, table, field, values):
        field_str = ", ".join(field)
        values_str = ", ".join(map(lambda x:"'{0}'".format(x), values))
        sql = "INSERT INTO {table} ({field}) VALUES ({values})".format(table=table, field=field, values=values)
        count = self._execute(sql)
        return count
    def _update_records(self, table, field, value, filter=None):
        if field.count != value.count:
            return 
        sql = "UPDATE {table} SET ".format(table)
        updates = ""
        for i in field.count:
            update += "{field} = '{value}', ".format(field=field[i], value=value[i])
        items.rstrip(", ")
        sql += update
        if filter is not None:
            sql += " WHERE {filter}".format(filter=filter)
        count = self._execute(sql)
        return count

    #パブリックメソッド
    #tableにusernameが存在するかチェック
    def exists_user(self, table, username):
        count = self._select_records(table=table, 
                                     field="COUNT(*)", 
                                     filter="username = '{0}'".format(username))
        return result[0][0] != 0L
    #期限切れのユーザをcheckテーブルから削除
    def delete_expire_users(self):
        del_users = self._select_records(table=self.check_table,
                                     field="username",
                                     relation=user_table,
                                     using="username",
                                     filter="expire_time < NOW()",
                                     group="username") #(('user1',),('user2',))
        for user in del_users:
            logging.info("delete user: " + user[0])
            self._delete_records(table=self.check_table, 
                                filter="username={0}".format(user[0]))
    #発行後のユーザの有効化
    def activate_user(self, username):
        if not self.exists_user(self.user_table, username):
            return False
        password = self._select_records(table=self.user_table, 
                                        field="password", 
                                        filter="username = '{0}'".format(username))[0][0]
        self._update_records(table=self.user_table, 
                             field=("activate_time", "expire_time" ), 
                             value=("NOW()", "NOW() + INTERVAL 8 HOUR"))
        self._insert_record(table=self.check_table, 
                            field=("username", "attribute", "op", "value"), 
                            values=(username, "Cleartext-Password", ":=", password))
    #TODO
    def auth_user_check(self):
        pass
    #ユーザを発行してデータベース登録
    def issue_user(self):
        #データベースに重複がなくなるまでランダム作成
        while True:
            #10文字のユーザ名とパスワードの生成
            username = "".join([random.choice(self.__source_char) for x in xrange(10)])
            password = "".join([random.choice(self.__source_char) for x in xrange(10)])
            logging.debug("username = " + username)
            logging.debug("password = " + password)
            exists = self.exists_user(self.user_table, username)
            #ユーザがテーブルに存在しないとき
            if not exists:
                result = self._insert_record(table=user_table, 
                                             field=("username", "password", "issue_time"), 
                                             values=(username, password, "NOW()"))
                return (username, password)

    #def is_authenticated(self, user):
    #    user_table = self._execute(self._SELECT_USER_TABLE_SQL)
    #    for row in user_table:
    #        if(row[0] == user and row[1] == ""):
    #             return False
    #    return True