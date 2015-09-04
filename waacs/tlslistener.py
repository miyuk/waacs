# -*- coding: utf-8 -*-
import socket
import ssl
import logging
logger = logging.getLogger(__name__)
import threading
import time
import tlsclient
class TlsListener(object):
    def __init__(self, listen_address, listen_port, certfile, keyfile, ca_certs):
        self.listen_address = listen_address
        self.listen_port = listen_port
        self.certfile = certfile
        self.keyfile = keyfile
        self.ca_certs = ca_certs
        self.server_sock = None
        self.is_started = False
    def start(self):
        self.server_sock = socket.socket()
        self.server_sock.bind((self.listen_address, self.listen_port))
        self.server_sock.listen(5)
        self.is_started = True
        logger.info("start tls listener on %s:%s", self.listen_address, self.listen_port)

    def accept(self):
        try:
            s, address = self.server_sock.accept()
            logger.info("receive from %s", address)
            conn_sock = ssl.wrap_socket(s,
                                        server_side=True,
                                        certfile=self.certfile,
                                        keyfile=self.keyfile,
                                        ca_certs=self.ca_certs,
                                        ssl_version=ssl.PROTOCOL_TLSv1)
            return tlsclient.TlsClient(conn_sock)
        except Exception as e:
            logger.error(e.message + str(e))
