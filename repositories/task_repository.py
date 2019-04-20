#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json

from dateutil import tz
from datetime import datetime

from models.list_model import ListModel
from models.task_model import TaskModel
from repositories.base_repository import BaseRedisRepository


class RedisTaskRepository(BaseRedisRepository):

    def __init__(self):
        BaseRedisRepository.__init__(self)

    @property
    def redis_connection(self):
        return super().redis_connection

    def __create_id(self):
        return super().create_id("tasks:index")

    def get_task(self, task_id) -> TaskModel:
        task_dict = self.redis_connection.hgetall("task:%s" % task_id)
        return self.unserialize(task_dict, TaskModel)

    def add_task(self, task_title: str, the_list: ListModel):
        task_id = self.__create_id()
        task = TaskModel(task_id, task_title, the_list.id_)
        self.redis_connection.incr("tasks:index")
        self.redis_connection.rpush("list:%s:tasks" % the_list.id_, task.id_)
        return self.save_task(task)

    def save_task(self, task):
        task_dict = self.serialize(task)
        return self.redis_connection.hmset("task:%s" % task.id_, task_dict)

    def get_task_from_list_number(self, the_list: ListModel, task_number_in_list: int) -> TaskModel:
        task_id = self.redis_connection.lindex("list:%s:tasks" % the_list.id_, task_number_in_list)
        if task_id:
            return self.get_task(task_id)
        else:
            return False

    def remove_task(self, task: TaskModel, task_type="tasks"):
        transaction = self.redis_connection.pipeline()
        transaction.lrem("list:%s:%s" % (task.list_id, task_type), 0, task.id_)
        transaction.delete("task:%s" % task.id_)
        return transaction.execute()

    def set_task_complete(self, task: TaskModel):
        transaction = self.redis_connection.pipeline()
        transaction.rpush("list:%s:tasks:completed" % task.list_id, task.id_)
        transaction.lrem("list:%s:tasks" % task.list_id, 0, task.id_)
        return transaction.execute()

    def task_local_datetime(self, task_timestamp):
        task_utc_datetime = datetime.utcfromtimestamp(task_timestamp)
        from_zone = tz.tzutc()
        to_zone = tz.tzlocal()
        task_utc_datetime = task_utc_datetime.replace(tzinfo=from_zone)
        local_datetime = task_utc_datetime.astimezone(to_zone)
        return local_datetime.strftime('%d.%m.%Y %H:%M:%S')

    def schedule_task(self, task: TaskModel, for_jid, timestamp):
        schedule_record = json.dumps({timestamp: for_jid})
        transaction = self.redis_connection.pipeline()
        transaction.sadd("scheduled", task.id_)
        transaction.rpush("scheduled:%s" % task.id_, schedule_record)
        return transaction.execute()

    def unschedule_task_at_all(self, task):
        transaction = self.redis_connection.pipeline()
        transaction.delete("scheduled:%s" % task.id_)
        transaction.srem("scheduled", task.id_)
        transaction.execute()

    def unschedule_task(self, task: TaskModel, for_jid, timestamp):
        schedule_record = json.dumps({timestamp: for_jid})
        result = self.redis_connection.lrem("scheduled:%s" % task.id_, 0, schedule_record)
        # Check timestamp list
        timestamp_list_length = self.redis_connection.llen("scheduled:%s" % task.id_)
        if timestamp_list_length == 0:
            transaction = self.redis_connection.pipeline()
            transaction.delete("scheduled:%s" % task.id_)
            transaction.srem("scheduled", task.id_)
            transaction.execute()
        return result

    def move_task(self, task: TaskModel, to_list):
        print(task)
        self.add_task(task.title, to_list)
        return self.remove_task(task)







