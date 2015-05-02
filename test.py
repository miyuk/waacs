import nfc.clf
import nfcconnection
import nfcserver
import nfcclient
import nfc.ndef
import logging
import nfc.snep
log = logging.getLogger(__name__)
import nfc
import os
import sys
import nfc.llcp
import threading
import nfc.dep
def main():
    logging.basicConfig()
    #logging.getLogger("nfc").setLevel(logging.DEBUG)
    log.info("open clf")
    clf = nfc.ContactlessFrontend("usb:054c:02e1")
    log.info("init clf")
    ba = lambda s: bytearray(s.decode("hex"))
    tta = {'cfg': None, 'uid': None}
    ttf = {'idm': ba("01FE"), 'pmm': None, 'sys': ba('FFFF')}
    targets = []
    targets.append(nfc.clf.TTA(br=106, **tta))
    targets.append(nfc.clf.TTF(br=212, **ttf))
    targets.append(nfc.clf.TTF(br=424, **ttf))
    log.info("close clf")
    raw_input()

def connected(llc):
    print llc
    server = nfcserver.NfcServer(llc)
    client = nfcclient.NfcClient(llc)
    server.start()
    
    raw_input()
    return True

main()
