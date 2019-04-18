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

    @property
    def xmpp_message(self):
        # Return the same value
        # as in the base class
        return super().xmmp_message

    @property
    def current_jid(self):
        # Return the same value
        # as in the base class
        return super().current_jid

    def route(self, message):
        self.add_reply_message(_(". - output existing lists"))
        self.add_reply_message(_(".<list_name> - add or display list, i.e. .tasks. Also makes list \"active\""))
        self.add_reply_message(_(". - display \"active\" list"))
        self.add_reply_message(_(".-<list_name> - delete whole list and it's tasks"))
        self.add_reply_message(" ")
        self.add_reply_message(_("Any message - adds task to active list"))
        self.add_reply_message(_("-<number> - delete task <number> from list, i.e. -1 deletes first task."))
        print(self.reply_message)
        return self.xmpp_message.reply(self.reply_message).send()
