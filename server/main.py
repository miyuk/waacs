# -*- coding: utf-8 -*-
import sys
import ConfigParser
import logging
import threading
#import userdb
import ssllistener
import socket
import waacs
def main(argc, argv):
    config = ConfigParser.ConfigParser()
    config.read("./server/server.cfg")
    listen_address = config.get("server" "ListenAddress")
    listen_port = config.getint("server", "ListenPort")
    set_logging()

    stop_event = threading.Event()
    interrupt_event = threading.Event()
    #db = userdb.UserDB(host, user, password)
    listener = ssllistener.SslListener(listen_address, listen_port)
    listener.start()
    while True:
        conn = listener.accept()
        data = ""
        while True:
            buffer = conn.read()
            if len(buffer) == 0:
                break
            data += buffer
        print data
def set_logging():
    loglevel = logging.INFO
    #if(argc == 2):
    #    loglevel = getattr(logging, argv[1].upper(), logging.NOTSET)
    format = "%(asctime)8s.%(msecs)03d|%(levelname)8s:%(message)s"
    date_format = "%H:%M:%S"
    logging.basicConfig(level=loglevel,
        format=format,
        datefmt=date_format)
    logging.getLogger("nfc").setLevel(loglevel)
   

if __name__ == '__main__':
    argv = sys.argv
    main(len(argv), argv)