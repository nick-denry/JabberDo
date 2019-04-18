#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import gettext
import logging
import ssl

from sleekxmpp import ClientXMPP

from components.config import Config
from routers.message_router import MessageRouter

# TODO: Replace with gettext install
# @see https://stackoverflow.com/questions/14946017/switch-translations-in-python-and-gettext
_ = gettext.gettext


class TasksBot(ClientXMPP):

    def __init__(self, jid: str, password: str):
        ClientXMPP.__init__(self, jid, password)
        self.add_event_handler("session_start", self.session_start)
        self.add_event_handler("message", self.message)
        logging.info(_(u"Bot init complete"))

    def session_start(self, event):
        self.send_presence()
        self.get_roster()

    def message(self, xmpp_message):
        if xmpp_message['type'] in ('chat', 'normal'):
            print(xmpp_message["body"])
            router = MessageRouter(xmpp_message)
            router.route(xmpp_message["body"])


if __name__ == '__main__':

    logging.basicConfig(level=logging.DEBUG,
                        format='%(levelname)-8s %(message)s')

    xmpp = TasksBot(Config.jid+"/bot", Config.password)
    if Config.protocol_sslv23:
        xmpp.ssl_version = ssl.PROTOCOL_SSLv23
    xmpp.auto_authorize = True  # TODO: Redo with custom subscription control?
    xmpp.auto_subscribe = True
    xmpp.registerPlugin('xep_0030')  # Service Discovery
    xmpp.registerPlugin('xep_0199')  # XMPP Ping

    # Connect to the XMPP server and start processing XMPP stanzas.
    if xmpp.connect():
        logging.info(_(u"Connected"))
        xmpp.process(block=True)
    else:
        logging.info(_(u"Can't connect"))
