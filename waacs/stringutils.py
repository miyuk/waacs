# -*- coding: utf-8 -*-
import datetime
TIME_FORMAT = "%Y-%m-%d %H:%M:%S"


def format_time(time):
    return datetime.datetime.strftime(time, TIME_FORMAT)


def parse_time(tstr):
    return datetime.datetime.strptime(tstr, TIME_FORMAT)
