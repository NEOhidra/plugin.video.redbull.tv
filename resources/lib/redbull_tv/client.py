__author__ = 'bromix'

from resources.lib.kodion import simple_requests as requests


class Client():
    def __init__(self):
        pass

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
        _headers = {}
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