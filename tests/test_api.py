# -*- cording: utf-8 -*-
from __future__ import unicode_literals

import os
import unittest
from slack_api_utils.client import Client

TOKEN = os.getenv("SLACK_API_TOKEN")


class ClientTest(unittest.TestCase):

    def setUp(self):
        self.client = Client(TOKEN)

    def test_get_user_dict(self):
        self.assertEqual(self.client._user_dict, {})
        self.assertIsInstance(
            self.client.get_user_dict(), dict)

    def test_get_channel_dict(self):
        self.assertEqual(self.client._channel_dict, {})
        self.assertIsInstance(
            self.client.get_channel_dict(), dict)

    def test_get_direct_dict(self):
        self.assertEqual(self.client._im_dict, {})
        self.assertIsInstance(
            self.client.get_direct_dict(), dict)

    def test_get_group_dict(self):
        self.assertEqual(self.client._group_dict, {})
        self.assertIsInstance(
            self.client.get_group_dict(), dict)


if __name__ == "__main__":
    unittest.main()
