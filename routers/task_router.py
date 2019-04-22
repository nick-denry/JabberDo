#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import gettext

from dateutil.parser import parse
from sleekxmpp.stanza.message import Message

from models.list_model import ListModel
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

    def __is_list_contain_only_digits(self, some_list: list) -> bool:
        for i in some_list:
            if not i.isdigit():
                return False
        return True

    def __set_single_task_complete(self, the_list: ListModel, task_sequential_number: int):
        task_number = int(task_sequential_number) - 1
        task = self.__task_repository.get_task_from_list_number(the_list, task_number_in_list=task_number)
        if not task:
            self.add_reply_message(
                _("No task #%s found in the %s list") % (task_sequential_number, the_list.name))
            return None
        self.__task_repository.set_task_complete(task)
        self.add_reply_message(_("Set task #%s complete") % task_sequential_number)

    def __set_multiple_tasks_complete(self, the_list: ListModel, task_sequential_numbers_list: list):
        print(task_sequential_numbers_list.split(" "))
        try:
            numbers_list = task_sequential_numbers_list.split(" ")
            print(numbers_list)
        except ValueError:
            self.add_reply_message(
                _("Please send task number or space-separated numbers (i.e. !33) to set task 33 complete."
                  " See current list tasks with ."))
            return None
        if not self.__is_list_contain_only_digits(numbers_list):
            self.add_reply_message(
                _("Please send numbers like !3 5 7 if you want to set multiple tasks complete."))
            return None
        # Reverse sort task numbers to complete tasks from the bottom of the list
        task_sequential_numbers_list_sorted = sorted(numbers_list, reverse=True)
        for task_sequential_number in task_sequential_numbers_list_sorted:
            self.__set_single_task_complete(the_list, task_sequential_number)

    def __set_task_complete_action(self, message):
        the_list = self.__list_repository.get_active(self.current_jid)
        if not the_list:
            self.add_reply_message(
                _("No active list found. See lists with .. or choose one by name .<list_name>"))
            return None
        if not message:
            self.add_reply_message(_("Text number(s) to comlete task(s) (◔_◔)"))
            return None
        if message.isdigit():
            self.__set_single_task_complete(the_list, message)
        else:
            self.__set_multiple_tasks_complete(the_list, message)

    def __remove_task_action(self, task_sequential_number):
        """
        Removes task number (sequential)
        :param sequential: str Sequential number of task in active list
        :return:
        """
        the_list = self.__list_repository.get_active(self.current_jid)
        if not the_list:
            self.add_reply_message(
                _("No active list found. See lists with .. or choose one by name .<list_name>"))
            return None
        if not task_sequential_number.isdigit():
            self.add_reply_message(_("Please send task number (i.e. #-33) to delete. See current list tasks with ."))
            return None
        task_number = int(task_sequential_number) - 1
        task = self.__task_repository.get_task_from_list_number(the_list, task_number_in_list=task_number)
        if not task:
            self.add_reply_message(_("No task #%s found in the %s list") % (task_sequential_number, the_list.name))
            return None
        self.__task_repository.remove_task(task)
        self.add_reply_message(_("Remove task #%s") % task_sequential_number)

    def __add_tasks_multiline_action(self, message):
        the_list = self.__list_repository.get_active(self.current_jid)
        if not the_list:
            self.add_reply_message(
                _("No active list found. See lists with .. or choose one by name .<list_name>"))
            return None
        for line in message.splitlines():
            self.__task_repository.add_task(line, the_list)
        self.add_reply_message(_("(ʘ‿ʘ)╯ alot of tasks added"))

    def __schedule_task_action(self, message):
        the_list = self.__list_repository.get_active(self.current_jid)
        if not the_list:
            self.add_reply_message(
                _("No active list found. See lists with .. or choose one by name .<list_name>"))
            return None
        try:
            task_sequential_number, date_andor_time = message.split(" ", 1)
        except ValueError:
            self.add_reply_message(_("No date time provided ٩(͡๏̯͡๏)۶"))
            return None
        if not task_sequential_number.isdigit():
            self.add_reply_message(
                _("Please send task number (i.e. #*33) to schedule. See current list tasks with ."))
            return None
        task_number = int(task_sequential_number)-1
        if not date_andor_time:
            self.add_reply_message(_("No date time provided ٩(͡๏̯͡๏)۶"))
            return None
        datetime = parse(date_andor_time)
        if not datetime:
            self.add_reply_message(_("Error convert date ಠ_ಠ"))
            return None
        timestamp = int(datetime.timestamp())
        task = self.__task_repository.get_task_from_list_number(the_list, task_number)
        if task:
            self.__task_repository.schedule_task(task, self.current_jid, timestamp)
            self.add_reply_message(_("⏰ Task #%s scheduled to %s") % (task_sequential_number, datetime))
        else:
            self.add_reply_message(
                _("No task #%s found in the %s list") % (task_number, the_list.name))

    def __unschedule_task_action(self, message):
        if not message:
            self.add_reply_message(_("٩(͡๏̯͡๏)۶ Please provide task number to unschedule ⏰"))
            return None
        if not message.isdigit():
            self.add_reply_message(_("⏰ can unschedule only task number ಠ_ಠ"))
            return None
        task = self.__task_repository.get_task(message)
        self.__task_repository.unschedule_task_at_all(task)


    def __update_task_action(self, message):
        the_list = self.__list_repository.get_active(self.current_jid)
        if not the_list:
            self.add_reply_message(
                _("No active list found. See lists with .. or choose one by name .<list_name>"))
            return None
        try:
            task_sequential_number, task_title = message.split(" ", 1)
        except ValueError:
            self.add_reply_message(_("No date time provided ٩(͡๏̯͡๏)۶"))
            return None
        if not task_sequential_number.isdigit():
            self.add_reply_message(
                _("Please send task number (i.e. #*33) to schedule. See current list tasks with ."))
            return None
        task_number = int(task_sequential_number)-1
        if not task_title:
            self.add_reply_message(_("No task provided ٩(͡๏̯͡๏)۶"))
            return None
        task = self.__task_repository.get_task_from_list_number(the_list, task_number)
        task.title = task_title
        self.__task_repository.save_task(task)
        self.add_reply_message(_("🖍️ Task %s updated") % task_sequential_number)

    def __move_task_to_list_action(self, message):
        current_list = self.__list_repository.get_active(self.current_jid)
        if not current_list:
            self.add_reply_message(
                _("No active list found. See lists with .. or choose one by name .<list_name>"))
            return None
        try:
            task_sequential_number, list_name_to_move = message.split(" ", 1)
        except ValueError:
            self.add_reply_message(_("No list name provided ٩(͡๏̯͡๏)۶"))
            return None
        if not task_sequential_number.isdigit():
            self.add_reply_message(
                _("Please send task number (i.e. #*33) to schedule. See current list tasks with ."))
            return None
        task_number = int(task_sequential_number) - 1
        if not list_name_to_move:
            self.add_reply_message(_("No list name provided ٩(͡๏̯͡๏)۶"))
            return None
        task = self.__task_repository.get_task_from_list_number(current_list, task_number)
        if not task:
            self.add_reply_message(
                _("No task #%s found in active list") % task_number)
            return None
        to_list = self.__list_repository.get_list_by_name(list_name_to_move)
        if not to_list:
            self.add_reply_message(_("List %s not found") % message)
            return None
        self.__task_repository.move_task(task, to_list)
        self.add_reply_message(
            _("➡️ Task %s moved to list %s") % (task_sequential_number, list_name_to_move))

    def __add_task_action(self, message):
        the_list = self.__list_repository.get_active(self.current_jid)
        if not the_list:
            self.add_reply_message(_("No active list found. See lists with .. or choose one by name .<list_name>"))
            return None
        self.__task_repository.add_task(message, the_list)
        self.add_reply_message(_("Task %s added to list %s") % (message, the_list.name))

    def route(self, message):
        command = self.extract_command(message)
        if command == "!":
            message = self.extract_command_message(command, message)
            self.__set_task_complete_action(message)
        elif command == "-":
            message = self.extract_command_message(command, message)
            self.__remove_task_action(task_sequential_number=message)
        elif command == ":":
            message = self.extract_command_message(command, message)
            if message:
                self.__add_tasks_multiline_action(message)
            else:
                self.add_reply_message(_("Text something (◔_◔)"))
        elif command == ">":
            message = self.extract_command_message(command, message)
            if message:
                self.__update_task_action(message)
            else:
                self.add_reply_message(_("Text number to edit task (◔_◔)"))
        elif command == "^":
            message = self.extract_command_message(command, message)
            if message:
                self.__move_task_to_list_action(message)
            else:
                self.add_reply_message(_("Text number and list to move task (◔_◔)"))
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
                    self.add_reply_message(_("Text number (◔_◔) to ⏰ the task"))
        else:
            # Get active list and add task to it
            self.__add_task_action(message)
        print(self.reply_message)
        return self.xmpp_message.reply(self.reply_message).send()
