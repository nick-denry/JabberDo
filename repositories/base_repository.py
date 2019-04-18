#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import redis

from components.config import Config


class BaseRedisRepository:

    def __init__(self):
        config = Config().config
        redis_host = config["redis_db"]["host"]
        redis_port = config["redis_db"]["port"]
        redis_db = config["redis_db"]["db"]
        # @see https://stackoverflow.com/a/25958063
        self.__r = redis.Redis(host=redis_host, port=redis_port, db=redis_db, decode_responses=True)

    @property
    def redis_connection(self):
        return self.__r

    def create_id(self, index_name):
        result = self.__r.get(index_name)
        if result:
            return result
        else:
            return self.__r.incr(index_name)

    def serialize(self, obj, exclude_properties: list = []) -> dict:
        serialized = {}
        obj_dict = obj.__dict__.copy()
        for property_ in exclude_properties:
            del obj_dict[property_]
        for k, v in obj_dict.items():
            serialized[k] = str(v)
        return serialized

    def unserialize(self, obj_dict: dict, object_class) -> object:
        return object_class(**obj_dict)
