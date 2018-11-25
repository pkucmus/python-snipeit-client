import requests

from snipeit import exceptions


class Endpoint:

    def __init__(self, client):
        self.client = client

        self.default_headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'Authorization': 'Bearer {}'.format(client.jwt)
        }

    @property
    def url(self):
        return '{}/api/v1/{}'.format(self.client.base_url, self.PATH)

    def __call(self, method, url, params=None, json=None, headers=None):
        default_headers = self.default_headers.copy()
        if headers:
            default_headers.update(headers)
        try:
            response = method(
                url,
                json=json,
                params=params,
                headers=default_headers,
                verify=self.client.verify_https
            )
        except requests.HTTPError:
            raise exceptions.FailedToReachSnipeIt(
                'Could not reach Portainer: {}'.format(url)
            )

        response.raise_for_status()
        return response.json()

    def post(self, url, json, headers=None):
        return self.__call(requests.post, url, json=json, headers=headers)

    def put(self, url, json, headers=None):
        return self.__call(requests.put, url, json=json, headers=headers)

    def get(self, url, params=None, headers=None):
        return self.__call(
            requests.get,
            url,
            params=params,
            headers=headers
        )


class ListHardware(Endpoint):

    PATH = 'hardware'

    def __call__(self, params=None):
        if params is None:
            params = {}
        params.setdefault('limit', 50)
        params.setdefault('offset', 0)
        data = {'rows': []}
        while True:
            response = self.get(self.url, params=params)
            params['offset'] += params['limit']
            data['total'] = response['total']
            data['rows'] += response['rows']
            if len(data['rows']) >= response['total']:
                break
        return data


class GetHardwareByTag(Endpoint):

    PATH = 'hardware/bytag/{asset_tag}'

    def __call__(self, asset_tag):
        return self.get(self.url.format(asset_tag=asset_tag))


class UpdateHardware(Endpoint):

    PATH = 'hardware/{id}'

    def __call__(self, asset_id, payload):
        return self.put(self.url.format(id=asset_id), json=payload)
