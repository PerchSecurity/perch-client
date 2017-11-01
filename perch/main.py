import json
import re
import requests

from .endpoints import ENDPOINTS


class CrudBase(object):
    def get(self):
        raise NotImplementedError

    def create(self):
        raise NotImplementedError

    def update(self):
        raise NotImplementedError

    def delete(self):
        raise NotImplementedError


class EndpointCrud(CrudBase):
    def __init__(self, api, name=None, path=None, verbs=()):
        self.api = api
        self.name = name
        self.path = path
        for verb in verbs:
            setattr(self, self.verb_to_name(verb), self.build_request(verb))

    @staticmethod
    def verb_to_name(verb):
        verb = verb.lower()
        name_map = {
            'post': 'create',
            'put': 'update'
        }
        return name_map.get(verb, verb)

    def build_url(self, verb, **kwargs):
        path = self.path
        params = re.findall(':(.[a-z+_]*)/*', path)
        for param in params:
            arg = str(kwargs.get(param, ''))
            if not arg:
                if not path.endswith(param) or verb in ('put', 'delete',):
                    raise TypeError('Squwaaaak! The {} kwarg is required!'.format(param))
            path = path.replace(':' + param, arg)

        url = self.api.root_url + path.rstrip('/')
        return url

    def make_request(self, req, **kwargs):
        url = self.build_url(req.__name__, **kwargs)
        res = req(url, headers=self.api.headers, json=kwargs)
        if not str(res.status_code).startswith('2'):
            raise RuntimeError('Squwaaaak! The api returned an error!\n{}\n'.format(res.reason))
        body = res.json()
        return body

    def build_request(self, verb):
        req = getattr(requests, verb.lower())
        return lambda **kwargs: self.make_request(req, **kwargs)


class PerchAPIClient(object):
    API_TOKEN = ''
    ROOT_URL = 'https://api.perchsecurity.com'
    AUTH_ENDPOINT = '/auth/access_token'

    def __init__(self, endpoints=ENDPOINTS, root_url=ROOT_URL, **kwargs):
        self.headers = {}
        self.endpoints = endpoints
        self.root_url = root_url
        credentials = ('username', 'password',)
        for cred in credentials:
            cred_arg = kwargs.get(cred)
            if not cred_arg:
                raise TypeError("Squwaaaakkk! perchy needs a {} kwarg!".format(cred))
            setattr(self, cred, cred_arg)
        self.authenticate()
        self.setup_endpoints()

    def setup_endpoints(self):
        for endpoint in self.endpoints:
            setattr(self, endpoint['name'], EndpointCrud(self, **endpoint))

    @property
    def auth_payload(self):
        return {
            'username': self.username,
            'password': self.password,
        }

    def authenticate(self):
        auth_url = self.root_url + self.AUTH_ENDPOINT
        res = requests.post(auth_url, json=self.auth_payload)
        if res.status_code != 200:
            raise RuntimeError("Squwaaaakkk! Invalid login credentials!")
        body = res.json()
        self.headers['Authorization'] = 'Bearer {}'.format(body['access_token'])
        return res


