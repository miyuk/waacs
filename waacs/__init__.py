# -*- coding: utf-8 -*-
__version__ = "latest"

from waacs.parameter import Parameter
import logging
import datetime
logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())
logger.setLevel(logging.INFO)

TIME_FORMAT = "%Y-%m-%d %H:%M:%S"


def format_time(time):
    return datetime.datetime.strftime(time, TIME_FORMAT)


def parse_time(tstr):
    return datetime.datetime.strptime(tstr, TIME_FORMAT)
