#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import datetime
import gettext
import json

from sleekxmpp.stanza.message import Message

from components.config import Config

# TODO: Replace with gettext install
# @see https://stackoverflow.com/questions/14946017/switch-translations-in-python-and-gettext
_ = gettext.gettext


class ScheduleRouter:

    def __init__(self, xmpp_client):
        self.xmpp_client = xmpp_client
        if Config.db_type == Config.DB_TYPE_REDIS:
            from repositories.list_repository import RedisListRepository
            from repositories.task_repository import RedisTaskRepository
            self.__list_repository = RedisListRepository()
            self.__task_repository = RedisTaskRepository()


    def route(self):
        # TODO: Remove duplicated code between list and schedule router
        current_timestamp = int(datetime.datetime.now().timestamp())
        scheduled_tasks_info = self.__list_repository.get_scheduled_tasks_info()
        for task_info in scheduled_tasks_info:
            for task_id, task_params_str in task_info.items():
                task = self.__task_repository.get_task(task_id)
                task_list = self.__list_repository.get_list(task.list_id)
                for task_str in task_params_str:
                    task_params = json.loads(task_str)
                    for task_timestamp, for_jid in task_params.items():
                        task_timestamp =  int(task_timestamp)
                        if current_timestamp > task_timestamp:
                            task_datetime = self.__task_repository.task_local_datetime(task_timestamp)
                            m = Message()
                            m["to"] = for_jid
                            m["body"] = _("Reminder for task %s from list %s, scheduled at %s") % (task.title, task_list.name, task_datetime)
                            m['type'] = "chat"
                            self.xmpp_client.send(m)
                            self.__task_repository.unschedule_task(task, for_jid, task_timestamp)
