__author__ = 'bromix'

import unittest

from resources.lib.redbull_tv.client import Client


class TestClient(unittest.TestCase):
    def test_get_channels(self):
        client = Client()
        data = client.get_channels()
        pass

    pass
