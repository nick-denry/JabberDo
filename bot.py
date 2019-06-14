#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import gettext
import logging
import ssl

from sleekxmpp import ClientXMPP

from components.config import Config
from routers.message_router import MessageRouter
from routers.schedule_router import ScheduleRouter

# TODO: Replace with gettext install
# @see https://stackoverflow.com/questions/14946017/switch-translations-in-python-and-gettext
_ = gettext.gettext


class TasksBot(ClientXMPP):

    CHECK_TIME_TASK = "taskbot_check_time"
    CHECK_TIME_SECONDS = 59

    def __init__(self, jid: str, password: str):
        ClientXMPP.__init__(self, jid, password)
        self.add_event_handler("session_start", self.session_start)
        self.add_event_handler("message", self.message)
        logging.info(_(u"Bot init complete"))
        self.__schedule_router =  ScheduleRouter(self)

    def session_start(self, event):
        self.send_presence()
        self.get_roster()

    def message(self, xmpp_message):
        if xmpp_message['type'] in ('chat', 'normal'):
            router = MessageRouter(xmpp_message)
            router.route(xmpp_message["body"])

    def check_time(self):
        self.scheduler.remove(self.CHECK_TIME_TASK)
        self.scheduler.add(self.CHECK_TIME_TASK, self.CHECK_TIME_SECONDS, self.check_time)
        self.__schedule_router.route()



if __name__ == '__main__':

    logging.basicConfig(level=logging.DEBUG,
                        format='%(levelname)-8s %(message)s')

    xmpp = TasksBot(Config.jid+"/bot", Config.password)
    if Config.protocol:
        xmpp.ssl_version = getattr(ssl, Config.protocol)
    xmpp.auto_authorize = True  # TODO: Redo with custom subscription control?
    xmpp.auto_subscribe = True
    xmpp.registerPlugin('xep_0030')  # Service Discovery
    xmpp.registerPlugin('xep_0199')  # XMPP Ping

    xmpp.scheduler.add(xmpp.CHECK_TIME_TASK, xmpp.CHECK_TIME_SECONDS, xmpp.check_time)

    # Connect to the XMPP server and start processing XMPP stanzas.
    if xmpp.connect():
        logging.info(_(u"Connected"))
        xmpp.process(block=True)
    else:
        logging.info(_(u"Can't connect"))
