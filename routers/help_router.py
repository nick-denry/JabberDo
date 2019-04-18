#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import gettext

from sleekxmpp.stanza.message import Message

from routers.base_router import BaseRouter

# TODO: Replace with gettext install
# @see https://stackoverflow.com/questions/14946017/switch-translations-in-python-and-gettext
_ = gettext.gettext


class HelpRouter(BaseRouter):

    def __init__(self, xmpp_message: Message):
        BaseRouter.__init__(self, xmpp_message)

    def route(self, command, sender):
        pass
