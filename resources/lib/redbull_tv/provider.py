# -*- coding: utf-8 -*-
import datetime
import urlparse
from resources.lib.kodion.items import DirectoryItem, VideoItem, NextPageItem

__author__ = 'bromix'

from resources.lib import kodion
from resources.lib.redbull_tv.client import Client


class Provider(kodion.AbstractProvider):
    def __init__(self):
        kodion.AbstractProvider.__init__(self)
        self._local_map.update({'redbull.shows': 30500,
                                'redbull.films': 30501,
                                'redbull.videos': 30502,
                                'redbull.clips': 30503})
        self._client = None
        pass

    def get_client(self, context):
        if not self._client:
            self._client = Client()
            pass

        return self._client

    def get_wizard_supported_views(self):
        return ['default', 'episodes', 'movies', 'tvshows']

    def get_alternative_fanart(self, context):
        return self.get_fanart(context)

    def get_fanart(self, context):
        return context.create_resource_path('media', 'fanart.jpg')

    @kodion.RegisterProviderPath('^/(?P<path>.+)/$')
    def _on_path(self, context, re_match):
        path = re_match.group('path')
        offset = context.get_param('offset', None)
        limit = context.get_param('limit', None)

        client = self.get_client(context)
        return self._response_to_items(context, client.do_raw(path=path, offset=offset, limit=limit))

    def _response_to_items(self, context, response):
        client = self.get_client(context)

        def _get_image(_item, _name, _width=None, _height=None, fallback=''):
            _image = _item.get('images', {}).get(_name, {}).get('uri', '')
            if _image:
                if _width and _height:
                    _image = '%s/width=%d,height=%d' % (_image, _width, _height)
                    pass
                elif _width:
                    _image = '%s/width=%d' % (_image, _width)
                    pass
                elif _height:
                    _image = '%s/height=%d' % (_image, _height)
                    pass
                pass
            elif fallback:
                return fallback

            return _image

        def _get_path_from_url(_item, _name):
            url = _item.get('meta', {}).get('links', {}).get(_name, '')
            path = client.url_to_path(url)
            return path

        def _do_channel_item(_item):
            _title = _item['title']
            _image = _get_image(_item, 'portrait', _width=440)
            _fanart = _get_image(_item, 'background', _width=1280, _height=720, fallback=self.get_fanart(context))

            _path = _get_path_from_url(_item, 'self')
            _channel_item = DirectoryItem(_title, uri=context.create_uri([_path]), image=_image, fanart=_fanart)
            return _channel_item

        def _do_channel_content(_item):
            _result = []

            for _sub_category in ['shows', 'films', 'videos', 'clips']:
                _sub_category_path = _get_path_from_url(_item, _sub_category)
                if _sub_category_path:
                    _sub_category_item = DirectoryItem(context.localize(self._local_map['redbull.%s' % _sub_category]),
                                                       uri=context.create_uri([_sub_category_path]))
                    _result.append(_sub_category_item)
                    pass
                pass

            # sub channels
            _sub_channels = _item.get('sub_channels', [])
            for _sub_channel in _sub_channels:
                _channel_item = _do_channel_item(_sub_channel)
                _result.append(_channel_item)
                pass
            return _result

        def _do_show_item(_item):
            _title = _item['title']
            _image = _get_image(_item, 'portrait', _width=440)
            _fanart = _get_image(_item, 'background', _width=1280, _height=720, fallback=self.get_fanart(context))

            _path = _get_path_from_url(_item, 'episodes')
            _show_item = DirectoryItem(_title, uri=context.create_uri([_path]), image=_image, fanart=_fanart)
            return _show_item

        def _do_video_item(_item):
            _title = _item['title']
            _subtitle = _item.get('subtitle', '')
            if _subtitle:
                _title = '%s - %s' % (_title, _subtitle)
                pass
            _image = _get_image(_item, 'landscape', _width=440)

            # we try to get a nice background based on the show
            _show = _item.get('show', {})
            if not _show or _show is None:
                _show = {}
                pass
            _fanart = _get_image(_show, 'background', _width=1280, _height=720, fallback=self.get_fanart(context))

            _path = _get_path_from_url(_item, 'self')
            _video_item = VideoItem(_title, uri=context.create_uri([_path]), image=_image, fanart=_fanart)

            _plot = _item.get('long_description', '')
            _video_item.set_plot(_plot)

            _duration = _item.get('duration', '')
            if _duration:
                _duration = kodion.utils.datetime_parser.parse(_duration)
                _seconds = _duration.second
                _seconds += _duration.minute*60
                _seconds += _duration.hour*60*60
                _video_item.set_duration_from_seconds(_seconds)
                pass

            _published = _item.get('published_on', '')
            if _published:
                _published = kodion.utils.datetime_parser.parse(_published)
                if isinstance(_published, datetime.date):
                    _published = datetime.datetime(_published.year, _published.month, _published.day, 0, 0, 0, 0)
                    pass
                _video_item.set_aired_from_datetime(_published)
                _video_item.set_date_from_datetime(_published)
                _video_item.set_year(_published.year)
                _video_item.set_premiered_from_datetime(_published)
                pass

            _season = _item.get('season_number', 1)
            if _season and _season is not None:
                _video_item.set_season(int(_season))
                pass

            _episode = _item.get('episode_number', 1)
            if _episode and _episode is not None:
                _video_item.set_episode(int(_episode))
                pass
            return _video_item

        result = []

        response_type = response.get('type', '')
        # channel
        if response_type:
            if response_type == 'channel':
                result.extend(_do_channel_content(response))
            return result

        #channels
        channels = response.get('channels', [])
        for channel in channels:
            channel_item = _do_channel_item(channel)
            result.append(channel_item)
            pass

        #shows
        shows = response.get('shows', [])
        for show in shows:
            show_item = _do_show_item(show)
            result.append(show_item)
            pass
        if shows:
            context.set_content_type(kodion.constants.content_type.TV_SHOWS)
            pass

        #videos
        videos = response.get('videos', [])
        video_type = ''
        for video in videos:
            video_type = video.get('type', 'episode')
            video_item = _do_video_item(video)
            result.append(video_item)
            pass
        if video_type:
            if video_type == 'clip' or video_type == 'episode':
                context.set_content_type(kodion.constants.content_type.EPISODES)
                pass
            elif video_type == 'film':
                context.set_content_type(kodion.constants.content_type.MOVIES)
                pass
            pass

        #meta (next page)
        next_page = _get_path_from_url(response, 'next_page')
        if next_page:
            next_page_url = response.get('meta', {}).get('links', {}).get('next_page', '')
            next_page_url = next_page_url.split('?')
            if len(next_page_url) > 1:
                params = dict(urlparse.parse_qsl(next_page_url[1]))

                new_params = {}
                new_params.update(context.get_params())
                new_params.update(params)
                new_context = context.clone(new_params=new_params)
                current_page = int(context.get_param('page', '1'))
                next_page_item = NextPageItem(new_context, current_page, fanart=self.get_fanart(new_context))
                result.append(next_page_item)
                pass
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