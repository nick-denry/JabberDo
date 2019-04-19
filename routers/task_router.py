#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import gettext

from dateutil.parser import parse
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

    def __set_task_complete_action(self, task_sequential_number):
        if task_sequential_number.isdigit():
            the_list = self.__list_repository.get_active(self.current_jid)
            if the_list:
                task_number = int(task_sequential_number) - 1
                task = self.__task_repository.get_task_from_list_number(the_list, task_number_in_list=task_number)
                if task:
                    # self.__task_repository.remove_task(task)
                    self.__task_repository.set_task_complete(task)
                    self.add_reply_message(_("Set task #%s complete") % task_sequential_number)
                else:
                    self.add_reply_message(
                        _("No task #%s found in the %s list") % (task_sequential_number, the_list.name))
            else:
                self.add_reply_message(
                    _("No active list found. See lists with .. or choose one by name .<list_name>"))
        else:
            self.add_reply_message(
                _("Please send task number (i.e. #!33) to set complete. See current list tasks with ."))

    def __remove_task_action(self, task_sequential_number):
        """
        Removes task number (sequential)
        :param sequential: str Sequential number of task in active list
        :return:
        """
        if task_sequential_number.isdigit():
            the_list = self.__list_repository.get_active(self.current_jid)
            if the_list:
                task_number = int(task_sequential_number) - 1
                task = self.__task_repository.get_task_from_list_number(the_list, task_number_in_list=task_number)
                if task:
                    self.__task_repository.remove_task(task)
                    self.add_reply_message(_("Remove task #%s") % task_sequential_number)
                else:
                    self.add_reply_message(_("No task #%s found in the %s list") % (task_sequential_number, the_list.name))
            else:
                self.add_reply_message(
                    _("No active list found. See lists with .. or choose one by name .<list_name>"))
        else:
            self.add_reply_message(_("Please send task number (i.e. #-33) to delete. See current list tasks with ."))

    def __add_tasks_multiline_action(self, message):
        the_list = self.__list_repository.get_active(self.current_jid)
        if the_list:
            for line in message.splitlines():
                self.__task_repository.add_task(line, the_list)
            self.add_reply_message(_("(ʘ‿ʘ)╯ alot of tasks added"))
        else:
            self.add_reply_message(
                _("No active list found. See lists with .. or choose one by name .<list_name>"))

    def __schedule_task_action(self, message):
        try:
            task_sequential_number, date_andor_time = message.split(" ", 1)
            if task_sequential_number.isdigit():
                task_number = int(task_sequential_number)-1
                if date_andor_time:
                    datetime = parse(date_andor_time)
                    if datetime:
                        timestamp = int(datetime.timestamp())
                        the_list = self.__list_repository.get_active(self.current_jid)
                        task = self.__task_repository.get_task_from_list_number(the_list, task_number)
                        if task:
                            self.__task_repository.schedule_task(task, self.current_jid, timestamp)
                            self.add_reply_message(_("⏰ Task #%s scheduled to %s") % (task_number, datetime))
                        else:
                            self.add_reply_message(
                                _("No task #%s found in the %s list") % (task_number, the_list.name))
                    else:
                        self.add_reply_message(_("Error convert date ಠ_ಠ"))
                else:
                    self.add_reply_message(_("No date time provided ٩(͡๏̯͡๏)۶"))
            else:
                self.add_reply_message(
                    _("Please send task number (i.e. #*33) to schedule. See current list tasks with ."))
        except ValueError:
            self.add_reply_message(_("No date time provided ٩(͡๏̯͡๏)۶"))

    def __unschedule_task_action(self, message):
        if message:
            if message.isdigit():
                task = self.__task_repository.get_task(message)
                self.__task_repository.unschedule_task_at_all(task)
            else:
                self.add_reply_message(_("⏰ can unschedule only task number ಠ_ಠ"))
        else:
            self.add_reply_message(_("٩(͡๏̯͡๏)۶ Please provide task number to unschedule ⏰"))

    def route(self, message):
        command = self.extract_command(message)
        if command == "!":
            message = self.extract_command_message(command, message)
            self.__set_task_complete_action(task_sequential_number=message)
        elif command == "-":
            message = self.extract_command_message(command, message)
            self.__remove_task_action(task_sequential_number=message)
        elif command == ":":
            message = self.extract_command_message(command, message)
            if message:
                self.__add_tasks_multiline_action(message)
            else:
                self.add_reply_message(_("Text something (◔_◔)"))
        elif command == "*":
            message = self.extract_command_message(command, message)
            command = self.extract_command(message)
            if command == "-":
                message = self.extract_command_message(command, message)
                self.__unschedule_task_action(message)
            else:
                if message:
                    self.__schedule_task_action(message)
                else:
                    self.add_reply_message(_("Text something (◔_◔) to ⏰ the task"))
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
