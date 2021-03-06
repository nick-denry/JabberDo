#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import gettext

from sleekxmpp.stanza.message import Message

from routers.base_router import BaseRouter

translation = gettext.translation('help_router', localedir='i18n', languages=['ru'])
translation.install()


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
        self.add_reply_message(_(".. - output existing lists"))
        self.add_reply_message(_(".list_name - add or display list, i.e. `.tasks`. Also makes list \"active\"."))
        self.add_reply_message(_(". - display active list"))
        self.add_reply_message(_(".-- - clear tasks of the active list"))
        self.add_reply_message(_(".! - display completed tasks of the active list"))
        self.add_reply_message(_(".!- - clear completed tasks of the active list"))
        self.add_reply_message(_(".-list_name - delete list and all of its tasks"))
        self.add_reply_message(" ")
        self.add_reply_message(_("Any message - adds task to active list"))
        self.add_reply_message(_(":any_multiline_message - add multiple tasks from multiline message"))
        self.add_reply_message(_("!task_number [task_number] - move task(s) task_number to completed"))
        self.add_reply_message(_("-task_number - delete task task_number from list, i.e. -1 deletes first task."))
        self.add_reply_message(_(">task_number title - edit task task_number from current list, set it new title"))
        self.add_reply_message(_("^task_number list_name` - move task `task_umber` from current list to list_name list"))
        self.add_reply_message(" ")
        self.add_reply_message(_("*task_number time date - set reminder for task task_number to time/date"))
        self.add_reply_message(_(".* - list scheduled tasks"))
        print(self.reply_message)
        return self.xmpp_message.reply(self.reply_message).send()
