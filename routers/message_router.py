#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import gettext

from sleekxmpp.stanza.message import Message

from components.config import Config
from routers.base_router import BaseRouter
from routers.help_router import HelpRouter
from routers.list_router import ListRouter
from routers.task_router import TaskRouter


# TODO: Replace with gettext install
# @see https://stackoverflow.com/questions/14946017/switch-translations-in-python-and-gettext
_ = gettext.gettext

class MessageRouter(BaseRouter):

    def __init__(self, xmpp_message: Message):
        BaseRouter.__init__(self, xmpp_message)
        # Assign routers with top level commands
        self.__top_level_commands = {
            ".": ListRouter(self.xmpp_message),
            "#": TaskRouter(self.xmpp_message),
            "?": HelpRouter(self.xmpp_message)
        }

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

    # Top-level routing
    def route(self, message: str):
        # Check if jid is allowed first
        # TODO: allow users to invite another users
        if self.current_jid not in Config.allowed_jids:
            self.reply_message(_(u"Nope ;)"))
            self.xmpp_message.send()
            return None
        # Transfer commands to next handler
        self.__pass_to_router(message)

    # Pass message to a proper router
    def __pass_to_router(self, message: str):
        command = self.extract_command(message)
        if command in self.__top_level_commands:
            router = self.__top_level_commands[command]
            message = self.extract_command_message(command, message)
        else:
            # Task router used by default for not-in-list commands
            # Pass initial message for it
            router = self.__top_level_commands["#"]
        router.route(message)
