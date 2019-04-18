#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from models.list_model import ListModel
from repositories.base_repository import BaseRedisRepository
from repositories.task_repository import RedisTaskRepository


class RedisListRepository(BaseRedisRepository):

    def __init__(self):
        BaseRedisRepository.__init__(self)
        self.__tasks_repository = RedisTaskRepository()

    @property
    def redis_connection(self):
        return super().redis_connection

    def __get_id_by_name(self, list_name):
        list_id = self.redis_connection.zscore("lists:names", list_name)
        return int(list_id) if list_id else None

    def __create_id(self):
        return super().create_id("lists:index")

    def __get_list_tasks(self, list_id, tasks_type="tasks"):
        list_tasks_ids = self.redis_connection.lrange("list:%s:%s" % (list_id, tasks_type), 0, -1)
        tasks = []
        for task_id in list_tasks_ids:
            task = self.__tasks_repository.get_task(task_id)
            tasks.append(task)
        return tasks

    def is_list_exists(self, list_name):
        list_id = self.__get_id_by_name(list_name)
        return self.redis_connection.exists("list:%s" % list_id)

    def get_list_by_name(self, list_name):
        list_id = self.__get_id_by_name(list_name)
        return self.get_list(list_id)

    def get_list(self, list_id):
        list_dict = self.redis_connection.hgetall("list:%s" % list_id)
        if list_dict:
            the_list = self.unserialize(list_dict, ListModel)
            list_tasks = self.__get_list_tasks(the_list.id_)
            for task in list_tasks:
                the_list.add_task(task)
            list_completed_tasks = self.__get_list_tasks(the_list.id_, "tasks:completed")
            for task in list_completed_tasks:
                the_list.add_completed_task(task)
            return the_list
        else:
            return None

    def get_all_lists_names(self):
        return self.redis_connection.zrange("lists:names", 0, -1)

    def add_list(self, list_name):
        """
        Creates list if not exist
        :param list_name: str Name of the list to add
        :return: bool
        """
        list_id = self.__create_id()
        the_list = ListModel(list_id, list_name)
        list_dict = self.serialize(the_list, ["tasks", "completed_tasks"])
        self.redis_connection.zadd("lists:names", {the_list.name: the_list.id_})
        self.redis_connection.lpush("lists", the_list.id_)
        self.redis_connection.incr("lists:index")
        result = self.redis_connection.hmset("list:%s" % the_list.id_, list_dict)  # Update list itself
        return result

    def set_active(self, list_name, current_jid):
        if self.is_list_exists(list_name):
            list_id = self.__get_id_by_name(list_name)
            transaction = self.redis_connection.pipeline()
            transaction.sadd("list:%s:active_for" % list_id, current_jid)
            transaction.set("%s:active:list" % current_jid, list_id)
            return transaction.execute()
        return False

    def get_active(self, current_jid):
        list_id = self.redis_connection.get("%s:active:list" % current_jid)
        return self.get_list(list_id)

    def remove_list_completed_tasks(self, the_list):
        for task in the_list.completed_tasks[:]:  # [:] Iterate over list copy to delete from source list
            self.__tasks_repository.remove_task(task, "tasks:completed")
            the_list.remove_completed_task(task)
        self.redis_connection.delete("list:%s:tasks:completed" % the_list.id_)

    def remove_list_tasks(self, the_list):
        for task in the_list.tasks[:]:  # [:] Iterate over list copy to delete from source list
            self.__tasks_repository.remove_task(task)
            the_list.remove_task(task)
        self.redis_connection.delete("list:%s:tasks" % the_list.id_)

    def remove_list(self, list_name):
        # Remove lists tasks
        the_list = self.get_list_by_name(list_name)
        if the_list:
            self.remove_list_tasks(the_list)
            self.remove_list_completed_tasks(the_list)
            list_active_for = self.redis_connection.smembers("list:%s:active_for" % the_list.id_)
            # Remove list from active user lists
            transaction = self.redis_connection.pipeline()
            for user_jid in list_active_for:
                transaction.delete("%s:active:list" % user_jid)
            transaction.delete("list:%s:active_for" % the_list.id_)
            # Remove list from indexes and itself
            transaction.lrem("lists", 0, the_list.id_)
            transaction.zrem("lists:names", the_list.name)
            transaction.delete("list:%s" % the_list.id_)
            return transaction.execute()
        else:
            return False

    def get_scheduled_tasks_info(self):
        scheduled_ids = self.get_scheduled_tasks_ids()
        scheduled_tasks_info = []
        for task_id in scheduled_ids:
            task_info = self.redis_connection.lrange("scheduled:%s" % task_id, 0, -1)
            scheduled_tasks_info.append({task_id: task_info})
        return scheduled_tasks_info

    def get_scheduled_tasks_ids(self):
        return self.redis_connection.smembers("scheduled")


