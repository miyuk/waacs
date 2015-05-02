# -*- coding: utf-8 -*-
import sys
import ConfigParser
import nfcconnection
import logging
import threading
import sslclient
#_EXPIRY_TIME = datetime.timedelta(hours=8) #8 hours
#_OFFER_TIMEOUT = datetime.timedelta(seconds=10)
#_DEL_USER_INTERVAL = 1 * 60 # 1 minutes
def main(argc, argv):
    config = ConfigParser.ConfigParser()
    config.read("./client/client.cfg")
    ssid = config.get("client", "Ssid")
    server_address = config.get("client", "ServerAddress")
    user_id = config.get("client", "UserId")
    password = config.get("client", "Password")
    server_address = config.get("client", "ServerAddress")
    server_port = config.getint("client", "ServerPort")
    set_logging()

    stop_event = threading.Event()
    interrupt_event = threading.Event()
    #nfc_conn = nfcconnection.NfcConnection()
    #nfc_thread = threading.Thread(target=nfc_run)
    #nfc_thread.setDaemon(True)
    #nfc_thread.run()
    client = sslclient.SslClient(host=server_address, port=server_port)
    client.write("hello world")
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

def nfc_run():
    while not stop_event.is_set():
        nfc_interrupt_event.clear()
        nfc_conn.connect(send_offer_message)
def start():
    nfc_thread.start()

#スレッドを停止する
def stop():
    stop_event.set()
    interrupt_event.set()

#SNEP受信した時のコールバック
#def on_receive_cb(self, ndef_message):
#    logging.debug("on_receive_cb(): Strart")
#    if(ndef_message is None):
#        logging.error("no ndef message")
#        return
#    if(ndef_message.type == _MESSAGE_RECORD_TYPE):
#        logging.warn("record type is not MESSAGE_RECORD_TYPE: " + ndef_message.type)
#        return
#    payload = self.get_payload(ndef_message)
#    parameter = negotiation.NegotiationManager.parse_parameter(payload)
#    if(parameter.message_type == negotiation.NegotiationManager.MessageType.ACCEPT):
#        self.user_manager.regist_user(parameter.user_id, parameter.password, parameter.regist_time, parameter.expire_time)
def send_offer_message(self, llc):
    logging.debug("send_offer_message(): Start")
    #ユーザ情報を作成
    user_id, password = self.user_manager.gen_rand_user()
    #期限は8時間
    regist_time = datetime.datetime.now()
    expire_time = regist_time + self._EXPIRY_TIME
    required_info = "TODO"
    offer_param = negotiation.NegotiationManager.make_parameter(message_type = negotiation.NegotiationManager.MessageType.OFFER,
        ssid = self.ssid,
        user_id = user_id,
        password = password,
        regist_time = regist_time,
        expire_time = expire_time,
        required_info = required_info)
    self.nfc_manager.send_waacs_message(offer_param)
    self.user_manager.regist_user(user_id, password, regist_time, expire_time)
    return True

if __name__ == '__main__':
    argv = sys.argv
    main(len(argv), argv)