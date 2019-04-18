#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import time


class TaskModel:

    def __init__(self, id_: int, title: str, list_id: int, created: int = 0):
        self.id_ = id_
        self.list_id = list_id
        self.title = title
        self.created = created if created else int(time.time())
        # TODO: Add reminder date and time
