#!/usr/bin/env python3
# -*- coding: utf-8 -*-


class ListModel:

    tasks = []
    completed_tasks = []

    def __init__(self, id_: int, name: str):
        self.id_ = id_
        self.name = name
        self.tasks = []
        self.completed_tasks = []

    def add_task(self, task):
        self.tasks.append(task)

    def remove_task(self, task):
        self.tasks.remove(task)

    def add_completed_task(self, task):
        self.completed_tasks.append(task)

    def remove_completed_task(self, task):
        self.completed_tasks.remove(task)
