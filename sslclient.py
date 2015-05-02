# -*- coding: utf-8 -*-
import socket
import ssl
import logging
class SslClient(object):
    def __init__(self, host=None, port=0, sock=None):
        self.is_connected = False
        self.client_sock = None
        if sock is not None:
            self.client_sock = sock
            self.is_connected = True
        elif host is not None and port != 0:
            self.connect(host, port)
    
    def connect(self, host, port):
        if self.is_connected:
            logging.warning("already is_connected")
            return
        s = socket.socket()
        self.client_sock = ssl.wrap_socket(sock=s, 
                                    ssl_version=ssl.PROTOCOL_TLSv1)
        self.client_sock.connect((host, port))
        self.is_connected = True

    def close(self):
        if not self.is_connected:
            logging.warning("yet is_connected")
            return
        self.client_sock.close()
        self.is_connected = False
    def write(self, data):
        if not self.is_connected:
            return
        self.client_sock.write(data)

    def read(self):
        if not self.is_connected:
            return
        result = ""
        while True:
            data = self.client_sock.read()
            if len(data) == 0:
                break
            result += data
        return result