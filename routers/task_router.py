#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import gettext

from sleekxmpp.stanza.message import Message

from components.config import Config
from routers.base_router import BaseRouter

# TODO: Replace with gettext install
# @see https://stackoverflow.com/questions/14946017/switch-translations-in-python-and-gettext
_ = gettext.gettext


class TaskRouter(BaseRouter):

    def __init__(self, xmpp_message: Message):
        BaseRouter.__init__(self, xmpp_message)
        if Config.db_type == Config.DB_TYPE_REDIS:
            from repositories.list_repository import RedisListRepository
            from repositories.task_repository import RedisTaskRepository
            self.__list_repository = RedisListRepository()
            self.__task_repository = RedisTaskRepository()

    @property
    def xmpp_message(self):
        """
        Return the same value
        as in the base class
        :return:
        """
        return super().xmmp_message

    @property
    def reply_message(self):
        return super().reply_message

    def route(self, message):
        command = self.extract_command(message)
        if command == "!":
            message = self.extract_command_message(command, message)
            if message.isdigit():
                self.add_reply_message(_("Set task #%s complete") % message)
            else:
                self.add_reply_message(_("Please send task number (i.e. #!33). See current list tasks with ."))
        elif command == "-":
            message = self.extract_command_message(command, message)
            if message.isdigit():
                the_list = self.__list_repository.get_active(self.current_jid)
                if the_list:
                    task_number = int(message) - 1
                    task = self.__task_repository.get_task_from_list_number(the_list, task_number_in_list=task_number)
                    if task:
                        self.__task_repository.remove_task(task)
                        self.add_reply_message(_("Remove task #%s") % message)
                    else:
                        self.add_reply_message(_("No task #%s found in the %s list") % (message, the_list.name))
                else:
                    self.add_reply_message(
                        _("No active list found. See lists with .. or choose one by name .<list_name>"))
            else:
                self.add_reply_message(_("Please send task number (i.e. #!33). See current list tasks with ."))
        else:
            # Get active list and add task to it
            the_list = self.__list_repository.get_active(self.current_jid)
            if the_list:
                self.__task_repository.add_task(message, the_list)
                self.add_reply_message(_("Task %s added to list %s") % (message, the_list.name))
            else:
                self.add_reply_message(_("No active list found. See lists with .. or choose one by name .<list_name>"))
        print(self.reply_message)
        return self.xmpp_message.reply(self.reply_message).send()
