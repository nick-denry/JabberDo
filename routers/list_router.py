#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import datetime
import gettext
import json

from sleekxmpp.stanza.message import Message

from components.config import Config
from routers.base_router import BaseRouter

# TODO: Replace with gettext install
# @see https://stackoverflow.com/questions/14946017/switch-translations-in-python-and-gettext
_ = gettext.gettext


class ListRouter(BaseRouter):

    def __init__(self, xmpp_message: Message):
        BaseRouter.__init__(self, xmpp_message)
        if Config.db_type == Config.DB_TYPE_REDIS:
            from repositories.list_repository import RedisListRepository
            from repositories.task_repository import RedisTaskRepository
            self.__task_repository = RedisTaskRepository()
            self.__list_repository = RedisListRepository()

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

    def __display_list_tasks_action(self, the_list, no_tasks_message, tasks_type="tasks"):
        list_tasks_of_type = getattr(the_list, tasks_type)
        if list_tasks_of_type:
            for idx, task in enumerate(list_tasks_of_type):
                self.add_reply_message("%i. %s" % (idx + 1, task.title))
        else:
            self.add_reply_message(no_tasks_message)

    def __display_active_list_action(self):
        the_list = self.__list_repository.get_active(self.current_jid)
        if the_list:
            self.add_reply_message(_("Active list is %s") % the_list.name)
            no_tasks_messsage = _("List is empty. Add task to it by send some message.")
            self.__display_list_tasks_action(the_list, no_tasks_messsage)
        else:
            self.add_reply_message(_("No active list found. See lists with .. or choose one by name .<list_name>"))

    def __display_schedule_list_action(self):
        scheduled_tasks_info = self.__list_repository.get_scheduled_tasks_info()
        if scheduled_tasks_info:
            for task_info in scheduled_tasks_info:
                for task_id, task_params_str in task_info.items():
                    task = self.__task_repository.get_task(task_id)
                    for task_str in task_params_str:
                        task_params = json.loads(task_str)
                        for task_timestamp, for_jid in task_params.items():
                            task_timestamp = int(task_timestamp)
                            task_datetime = datetime.datetime.utcfromtimestamp(task_timestamp).strftime('%d.%m.%Y %H:%M:%S')
                            self.add_reply_message("%s: %s. %s" % (task_datetime, task.id_, task.title))
        else:
            self.add_reply_message(_("No ⏰ tasks"))

    def route(self, message: str):
        if message:
            command = self.extract_command(message)
            if command == ".":
                all_list_names = self.__list_repository.get_all_lists_names()
                if all_list_names:
                    self.add_reply_message(_("All the lists:"))
                    for list_name in all_list_names:
                        self.add_reply_message(list_name)
                else:
                    self.add_reply_message(_("No lists. Add one by typing .<list_name>"))
            elif command == '*':
                self.__display_schedule_list_action()
            elif command == "-":
                message = self.extract_command_message(command, message)
                command = self.extract_command(message)
                if command == "-":
                    the_list = self.__list_repository.get_active(self.current_jid)
                    if the_list:
                        self.add_reply_message(_("Clear tasks of the %s list") % the_list.name)
                        self.__list_repository.remove_list_tasks(the_list)
                    else:
                        self.add_reply_message(
                            _("No active list found. See lists with .. or choose one by name .<list_name>"))
                else:
                    if message:
                        # Delete list and remove from current jid active lists
                        result = self.__list_repository.remove_list(message)
                        if result:
                            self.add_reply_message(_("Delete list %s") % message)
                        else:
                            self.add_reply_message(_("List %s not found") % message)
                    else:
                        self.add_reply_message(_("Need a list name to delete"))
            elif command == "!":
                message = self.extract_command_message(command, message)
                command = self.extract_command(message)
                the_list = self.__list_repository.get_active(self.current_jid)
                # Clear completed tasks
                if command == "-":
                    self.__list_repository.remove_list_completed_tasks(the_list)
                    self.add_reply_message(_("Clear completed tasks of the %s list") % the_list.name)
                # Display completed tasks
                else:
                    self.add_reply_message(_("Completed tasks of the %s list:") % the_list.name)
                    no_tasks_messsage = _("No completed tasks for this list. Complete one with !<number>.")
                    self.__display_list_tasks_action(the_list, no_tasks_messsage, "completed_tasks")
            else:
                # Check if list exits
                is_list_exists = self.__list_repository.is_list_exists(message)
                # If not add
                if not is_list_exists:
                    self.__list_repository.add_list(message)
                    self.add_reply_message(_("Added list %s") % message)
                # Set active for current user & display
                self.__list_repository.set_active(message, self.current_jid)
                self.__display_active_list_action()
        else:
            # Display active list
            self.__display_active_list_action()

        print(self.reply_message)
        return self.xmpp_message.reply(self.reply_message).send()
