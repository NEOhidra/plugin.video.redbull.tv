__author__ = 'bromix'

from resources.lib import kodion
from resources.lib.redbull_tv import Provider

import unittest


class TestProvider(unittest.TestCase):
    def test_on_root(self):
        provider = Provider()

        path = kodion.utils.create_path('/')
        context = kodion.Context(path=path)
        result = provider.navigate(context)
        items = result[0]
        pass

    pass