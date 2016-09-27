# -*- coding: utf-8 -*-
from socket import socket
import ssl
import logging
logger = logging.getLogger(__name__)


class TlsClient(object):

    def __init__(self, sock=None):
        if sock != None:
            self.client_sock = sock
            self.is_connected = True
        else:
            self.client_sock = ssl.wrap_socket(sock=socket(),
                                               ssl_version=ssl.PROTOCOL_TLSv1)
            self.is_connected = False

    def connect(self, host, port):
        if self.is_connected:
            logger.warn("already connected")
            return
        self.client_sock.connect((host, port))
        self.is_connected = True
        logger.info("connect to %s:%s", host, port)

    def close(self):
        if not self.is_connected:
            logger.warn("no connected")
            return
        self.client_sock.close()
        self.is_connected = False
        logger.info("close connect")

    def write(self, data):
        if not self.is_connected:
            logger.warn("no connected")
            return
        self.client_sock.write(data)
        logger.info("write data: \"%s\"", data)

    def read(self):
        if not self.is_connected:
            logger.warn("no connected")
            return
        data = self.client_sock.read()
        logger.info("read data: \"%s\"", data)
        return data
