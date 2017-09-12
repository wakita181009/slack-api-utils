# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import sys
import time
import logging
from slacker import Slacker, Error

from utils import TimeRange

logger = logging.getLogger("slack-api-utils")
logger.setLevel(logging.DEBUG)

# And always display on console
stderr_log_handler = logging.StreamHandler()
logger.addHandler(stderr_log_handler)

DEFAULT_TIMEOUT = 10


class Client(Slacker):
    def __init__(self, token, **kwargs):
        super(Client, self).__init__(token, **kwargs)
        self._user_dict = {}
        self._channel_dict = {}
        self._im_dict = {}
        self._mpim_dict = {}
        self._group_dict = {}

    @staticmethod
    def get_id_by_name(dic, name):
        return {v: k for k, v in dic.items()}.get(name)

    @staticmethod
    def _res_list_body(api_end_point):
        try:
            res = api_end_point.list().body
        except Error as e:
            logger.error("fail to get list: %s" % e.message)
            return

        if not res["ok"]:
            logger.error("fail to get list: %s" % res.get("error", ""))
            return

        return res

    def get_user_name_by_id(self, user_id):
        return self.get_user_dict().get(user_id)

    def get_user_id_by_name(self, user_name):
        return self.get_id_by_name(self.get_user_dict(), user_name)

    def get_user_dict(self):
        if not self._user_dict:
            res = self._res_list_body(self.users)
            if not res["ok"]:
                return

            members = res["members"]
            for m in members:
                self._user_dict[m["id"]] = m["name"]

        return self._user_dict

    def get_channel_name_by_id(self, channel_id):
        return self.get_channel_dict().get(channel_id)

    def get_channel_id_by_name(self, channel_name):
        return self.get_id_by_name(self.get_channel_dict(), channel_name)

    def get_channel_dict(self):
        if not self._channel_dict:
            res = self._res_list_body(self.channels)
            if not res["ok"]:
                return

            channels = res["channels"]
            for c in channels:
                self._channel_dict[c["id"]] = c["name"]

        return self._channel_dict

    def get_direct_name_by_id(self, direct_id):
        return self.get_direct_dict().get(direct_id)

    def get_direct_id_by_name(self, direct_name):
        return self.get_id_by_name(self.get_direct_dict(), direct_name)

    def get_direct_dict(self):
        if not self._im_dict:
            res = self._res_list_body(self.im)
            if not res["ok"]:
                return

            ims = res["ims"]
            for i in ims:
                self._im_dict[i["id"]] = self.get_user_name_by_id(i["user"])

        return self._im_dict

    def get_mpdirect_name_by_id(self, mpdirect_id):
        return self.get_mpdirect_dict().get(mpdirect_id)

    def get_mpdirect_id_by_name(self, mpdirect_name):
        return self.get_id_by_name(self.get_mpdirect_dict(), mpdirect_name)

    def get_mpdirect_dict(self):
        if not self._mpim_dict:
            res = self._res_list_body(self.mpim)
            if not res["ok"]:
                return

            mpims = res["groups"]
            for mpim in mpims:
                self._mpim_dict[mpim["id"]] = set([self.get_user_name_by_id(user_id) for user_id in mpim["members"]])

        return self._mpim_dict

    def get_group_name_by_id(self, group_id):
        return self.get_group_dict().get(group_id)

    def get_group_id_by_name(self, group_name):
        return self.get_id_by_name(self.get_group_dict(), group_name)

    def get_group_dict(self):
        if not self._group_dict:
            res = self._res_list_body(self.groups)
            if not res["ok"]:
                return

            groups = res["groups"]
            for g in groups:
                self._group_dict[g["id"]] = g["name"]

        return self._group_dict

    def _get_user_name(self, message):
        if message.get("user"):
            user_id = message.get("user")
            return self.get_user_name_by_id(user_id)
        elif message.get("username"):
            return message.get("username")
        else:
            return "_"

    def get_messages(self, channel_name=None, direct_name=None, group_name=None, user_name=None,
                     bot=False, start_time=None, end_time=None):
        _channel_id = None
        _user_id = None
        _api_end_point = None

        # If channel's name is supplied
        if channel_name:
            _channel_id = self.get_channel_id_by_name(channel_name)
            _api_end_point = self.channels.history

        # If DM's name is supplied
        if direct_name:
            _channel_id = self.get_direct_id_by_name(direct_name)
            _api_end_point = self.im.history

        # If channel's name is supplied
        if group_name:
            _channel_id = self.get_group_id_by_name(group_name)
            _api_end_point = self.groups.history

        if _channel_id is None:
            sys.exit("Channel, direct message or private group not found")

        # If user's name is also supplied
        if user_name:
            # A little bit tricky here, we use -1 to indicates `--user=*`
            if user_name == "*":
                _user_id = -1
            else:
                _user_id = self.get_user_id_by_name(user_name)

            if _user_id is None:
                sys.exit("User not found")

        # Delete messages on certain channel
        _time_range = TimeRange(start_time, end_time)
        for message in self._get_message_history(
                _channel_id, _time_range, _api_end_point, _user_id, bot):
            yield message["text"]

    def delete_messages(self, channel_name=None, direct_name=None, group_name=None, user_name=None,
                        bot=False, perform=False, start_time=None, end_time=None):
        _channel_id = None
        _user_id = None
        _api_end_point = None

        # If channel's name is supplied
        if channel_name:
            _channel_id = self.get_channel_id_by_name(channel_name)
            _api_end_point = self.channels.history

        # If DM's name is supplied
        if direct_name:
            _channel_id = self.get_direct_id_by_name(direct_name)
            _api_end_point = self.im.history

        # If channel's name is supplied
        if group_name:
            _channel_id = self.get_group_id_by_name(group_name)
            _api_end_point = self.groups.history

        if _channel_id is None:
            sys.exit("Channel, direct message or private group not found")

        # If user's name is also supplied
        if user_name:
            # A little bit tricky here, we use -1 to indicates `--user=*`
            if user_name == "*":
                _user_id = -1
            else:
                _user_id = self.get_user_id_by_name(user_name)

            if _user_id is None:
                sys.exit("User not found")

        # Delete messages on certain channel
        _time_range = TimeRange(start_time, end_time)
        for message in self._get_message_history(
                _channel_id, _time_range, _api_end_point, _user_id, bot):
            # Delete one message
            self.delete_one_message_on_channel(_channel_id, message, perform)

    @staticmethod
    def _get_message_history(channel_id, time_range, api_end_point, user_id=None, bot=False):
        oldest = time_range.start_time
        latest = time_range.end_time

        has_more = True
        while has_more:
            res = api_end_point(channel_id, latest, oldest).body
            if not res["ok"]:
                sys.exit(1)

            messages = res["messages"]
            has_more = res["has_more"]
            if len(messages) == 0:
                break

            for message in messages:
                latest = message["ts"]

                # User messages
                if message["type"] == "message":
                    # If it's a normal user message
                    if message.get("user"):
                        # message if user_name matched or `--user=*`
                        if message.get("user") == user_id or user_id == -1:
                            yield message

                    # Bot messages
                    if bot and message.get("subtype") == "bot_message":
                        yield message

                # Exceptions
                else:
                    logger.error("Weird message")

    def delete_one_message_on_channel(self, channel_id, message, perform=False):
        if perform:
            try:
                self.chat.delete(channel_id, message["ts"])
            except Error:
                time.sleep(2)
                logger.error("Failed to delete ->")
                logger.error(message)
                return

            time.sleep(3)
            logger.warning("Deleted message -> "
                           + self._get_user_name(message)
                           + " : %s"
                           , message.get("text", ""))

        else:
            logger.warning("Will delete message -> "
                           + self._get_user_name(message)
                           + " :  %s"
                           , message.get("text", ""))

    def invite_group(self, group_id=None, group_name=None, user_id=None, user_name=None):
        channel_id = group_id or self.get_group_id_by_name(group_name)
        user_id = user_id or self.get_user_id_by_name(user_name)

        if not channel_id or not user_id:
            sys.exit("group_id or user_id not found")

        res = self.groups.invite(channel=channel_id, user=user_id).body
        if not res["ok"]:
            logger.error(res["error"])
            return res["ok"], res["error"]

        else:
            return res["ok"], "success"

    def kick_group(self, group_id=None, group_name=None, user_id=None, user_name=None):
        channel_id = group_id or self.get_group_id_by_name(group_name)
        user_id = user_id or self.get_user_id_by_name(user_name)

        res = self.groups.kick(channel=channel_id, user=user_id).body
        if not res["ok"]:
            return res["ok"], res["error"]

        else:
            return res["ok"], "success"
