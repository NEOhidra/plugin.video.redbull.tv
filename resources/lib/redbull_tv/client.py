__author__ = 'bromix'

from resources.lib.kodion import simple_requests as requests


class Client():
    API_URL = 'https://api.redbull.tv/v1/'

    def __init__(self, limit=None):
        self._limit = limit
        pass

    def url_to_path(self, url):
        url = url.split('?')[0]
        if url.startswith(self.API_URL):
            url = url.replace(self.API_URL, '')
            pass
        if not url.endswith('/'):
            url += '/'
            pass
        return url

    def search(self, query, offset=None, limit=None):
        params = {'search': query}
        if offset or offset is not None:
            params['offset'] = str(offset)
            pass
        if self._limit or self._limit is not None:
            params['limit'] = str(self._limit)
            pass
        if limit or limit is not None:
            params['limit'] = str(limit)
            pass
        return self._perform_v1_request(path='search', params=params)

    def do_raw(self, path, offset=None, limit=None):
        params = {}
        if offset or offset is not None:
            params['offset'] = str(offset)
            pass
        if self._limit or self._limit is not None:
            params['limit'] = str(self._limit)
            pass
        if limit or limit is not None:
            params['limit'] = str(limit)
            pass
        return self._perform_v1_request(path=path, params=params)

    def get_channels(self):
        return self._perform_v1_request(path='channels')

    def _perform_v1_request(self, method='GET', headers=None, path=None, post_data=None, params=None,
                            allow_redirects=True):
        # params
        if not params:
            params = {}
            pass
        _params = {}
        _params.update(params)

        # headers
        if not headers:
            headers = {}
            pass
        _headers = {'User-Agent': 'Dalvik/2.1.0 (Linux; U; Android 5.0.1; GT-I9505 Build/LRX22C)',
                    'Host': 'api.redbull.tv',
                    'Connection': 'Keep-Alive',
                    'Accept-Encoding': 'gzip'}
        _headers.update(headers)

        # url
        _url = 'https://api.redbull.tv/v1/%s' % path.strip('/')

        result = None

        if method == 'GET':
            result = requests.get(_url, params=_params, headers=_headers, verify=False, allow_redirects=allow_redirects)
            pass
        elif method == 'POST':
            _headers['content-type'] = 'application/json'
            result = requests.post(_url, json=post_data, params=_params, headers=_headers, verify=False,
                                   allow_redirects=allow_redirects)
            pass
        elif method == 'PUT':
            _headers['content-type'] = 'application/json'
            result = requests.put(_url, json=post_data, params=_params, headers=_headers, verify=False,
                                  allow_redirects=allow_redirects)
            pass
        elif method == 'DELETE':
            result = requests.delete(_url, params=_params, headers=_headers, verify=False,
                                     allow_redirects=allow_redirects)
            pass

        if result is None:
            return {}

        if result.headers.get('content-type', '').startswith('application/json'):
            return result.json()
        pass

    pass