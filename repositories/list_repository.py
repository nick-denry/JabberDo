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

    def __get_list_tasks(self, list_id):
        list_tasks_ids = self.redis_connection.lrange("list:%s:tasks" % list_id, 0, -1)
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
        # TODO: Populate tasks for list
        list_dict = self.redis_connection.hgetall("list:%s" % list_id)
        if list_dict:
            the_list = self.unserialize(list_dict, ListModel)
            the_list.tasks = self.__get_list_tasks(the_list.id_)
            return the_list
        else:
            return None

    def get_all_lists_names(self):
        return self.redis_connection.zrange("lists:names", 0, -1)

    def add_list(self, list_name):
        """
        Creates list if not exist
        :param the_list:
        :return:
        """
        list_id = self.__create_id()
        the_list = ListModel(list_id, list_name)
        list_dict = self.serialize(the_list, ["tasks"])
        self.redis_connection.zadd("lists:names", {the_list.name: the_list.id_})
        self.redis_connection.lpush("lists", the_list.id_)
        self.redis_connection.incr("lists:index")
        result = self.redis_connection.hmset("list:%s" % the_list.id_, list_dict)  # Update list itself
        return result

    def set_active(self, list_name, current_jid):
        if self.is_list_exists(list_name):
            list_id = self.__get_id_by_name(list_name)
            return self.redis_connection.set("%s:active:list" % current_jid, list_id)
        return False

    def get_active(self, current_jid):
        list_id = self.redis_connection.get("%s:active:list" % current_jid)
        return self.get_list(list_id)

    def delete_list(self, list_name, current_jid):
        pass
