# -*- coding: utf-8 -*-
import socket
import ssl
import logging
import sslclient
class SslListener(object):
    def __init__(self, address, port):
        self.address = address
        self.port = port
        self.server_sock = None
        #ssl.SSLSocket.__init__(self,
        #                      sock=base,
        #                      server_side=True,
        #                      ssl_version=ssl.PROTOCOL_TLSv1,
        #                      ca_certs=ca_certs
        #                      )
        self.is_started = False

    def start(self):
        if self.is_started:
            return
        self.server_sock = socket.socket()
        self.server_sock.bind((self.address, self.port))
        self.server_sock.listen(5)
        self.is_started = True
    def stop(self):
        if not self.is_started:
            return
        self.server_sock.shutdown(socket.SHUT_RDWR)
        self.server_sock.close()
        self.is_started = False
    def accept(self):
        s, address = self.server_sock.accept()
        conn_sock = ssl.wrap_socket(sock=s,
                                    ssl_version=ssl.PROTOCOL_TLSv1)
        conn_ssl = sslclient.SslClient(sock=conn_sock)
        return conn_ssl

    #def connect(self, address, port):
    #    if self.is_connected:
    #        logging.warning("already connected")
    #        return None
    #    self.connect(address, port)
    #    self.is_connected = True
    #    return True
    #def send_command(self, command):
    #    command = command + "\r\n"
    #    self.write(command)
    #    result = ""
    #    while True:
    #        data = self.read()
    #        if length(data) == 0:
    #            break
    #        result += data
    #    return result

    #def disconnect(self):
    #    if not self.is_connected:
    #        logging.warning("yet connected")
    #        return
    #    self.close()
    #    self.is_connected = False
    #def receive_command(self):
    #    pass