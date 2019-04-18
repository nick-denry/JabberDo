#!/usr/bin/env python
# -*- coding: utf-8 -*-

import yaml

config = yaml.safe_load(open("config/main-local.yml"))


class Config:

    DB_TYPE_REDIS = "redis"

    jid = config["bot_account"]["jid"]
    password = config["bot_account"]["password"]
    port = config["bot_account"]["port"]
    protocol_sslv23 = bool(config["bot_account"]["PROTOCOL_SSLv23"])

    db_type = config["db"]["type"]

    allowed_jids = config["allowed_jids"]

    def __init__(self):
        self.config = config
