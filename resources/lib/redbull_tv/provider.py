# -*- coding: utf-8 -*-
from resources.lib.kodion.items import DirectoryItem

__author__ = 'bromix'

from resources.lib import kodion
from resources.lib.redbull_tv.client import Client


class Provider(kodion.AbstractProvider):
    def __init__(self):
        kodion.AbstractProvider.__init__(self)
        self._local_map.update({'redbull.bla': 30500})
        self._client = None
        pass

    def get_client(self, context):
        if not self._client:
            self._client = Client()
            pass

        return self._client

    def get_alternative_fanart(self, context):
        return self.get_fanart(context)

    def get_fanart(self, context):
        return context.create_resource_path('media', 'fanart.jpg')

    def _response_to_items(self, context, response):
        result = []

        #channels
        channels = response.get('channels', [])
        for channel in channels:
            title = channel['title']
            image = channel.get('images', {}).get('portrait', {}).get('uri', self.get_fanart(context))
            fanart = channel.get('images', {}).get('background', {}).get('uri', self.get_fanart(context))

            channel_item = DirectoryItem(title, uri='', image=image, fanart=fanart)
            result.append(channel_item)
            pass

        return result

    def on_root(self, context, re_match):
        result = []

        client = self.get_client(context)

        # channels
        result.extend(self._response_to_items(context, client.get_channels()))

        # search
        search_item = kodion.items.SearchItem(context, image=context.create_resource_path('media', 'search.png'),
                                              fanart=self.get_fanart(context))
        result.append(search_item)

        return result

    pass