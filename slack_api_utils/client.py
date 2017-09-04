# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import logging
from slacker import Slacker, Error

logger = logging.getLogger("slack-api-utils")
logger.setLevel(10)

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
        self._group_dict = {}

    @staticmethod
    def get_id_by_name(dic, name):
        return {v: k for k, v in dic.items()}.get(name)

    def get_user_name_by_id(self, user_id):
        return self.get_user_dict().get(user_id)

    def get_user_id_by_name(self, user_name):
        return self.get_id_by_name(self.get_user_dict(), user_name)

    def get_user_dict(self):
        if not self._user_dict:
            try:
                res = self.users.list().body
            except Error as e:
                logger.error("fail to get user list: %s" % e.message)
                return

            if not res["ok"]:
                logger.error("fail to get user list: %s" % res.get("error", ""))
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
            try:
                res = self.channels.list().body
            except Error as e:
                logger.error("fail to get channel list: %s" % e.message)
                return

            if not res["ok"]:
                logger.error("fail to get channel list: %s" % res.get("error", ""))
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
            try:
                res = self.im.list().body
            except Error as e:
                logger.error("fail to get im list: %s" % e.message)
                return

            if not res["ok"]:
                logger.error("fail to get im list: %s" % res.get("error", ""))
                return

            ims = res["ims"]
            for i in ims:
                self._im_dict[i["id"]] = self.get_user_name_by_id(i["user"])

        return self._im_dict

    def get_group_name_by_id(self, group_id):
        return self.get_group_dict().get(group_id)

    def get_group_id_by_name(self, group_name):
        return self.get_id_by_name(self.get_group_dict(), group_name)

    def get_group_dict(self):
        if not self._group_dict:
            try:
                res = self.groups.list().body
            except Error as e:
                logger.error("fail to get group list: %s" % e.message)
                return

            if not res["ok"]:
                logger.error("fail to get group list: %s" % res.get("error", ""))
                return

            groups = res["groups"]
            for g in groups:
                self._group_dict[g["id"]] = g["name"]

        return self._group_dict
