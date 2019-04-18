#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from sleekxmpp.jid import JID

from sleekxmpp.stanza.message import Message


class BaseRouter:

    def __init__(self, xmpp_message: Message):
        self.__xmpp_message = xmpp_message
        self.__current_jid = JID(xmpp_message["from"]).bare
        self.__reply_message = ""

    @property
    def xmmp_message(self):
        """
        Protect xmpp_message from changing
        :return:
        """
        return self.__xmpp_message

    @property
    def current_jid(self):
        """
        Protect current_jid from changing
        :return:
        """
        return self.__current_jid

    @property
    def reply_message(self):
        return self.__reply_message

    def add_reply_message(self, message_body):
        self.__reply_message += "%s\n" % message_body

    def extract_command(self, message: str) -> str:
        """
        Extract next command from message
        :param str message: current routing level message
        :return: str
        """
        try:
            command = message[0]
        except IndexError:
            command = None
        return command

    def extract_command_message(self, command: str, message: str) -> str:
        """
        Extract params for command from message
        :param str command: Current command
        :param srt message:Curernt message
        :return:
        """
        return message.replace(command, "", 1)

    def get_next_command(self, command, message):
        command_message = self.extract_command_message(command, message)
        next_command = self.extract_command(command_message)
        return next_command
