import requests


class PerchAPIClient(object):
    API_TOKEN = ''
    ROOT_URL = 'https://api.perchsecurity.com'

    def __init__(self, **kwargs):
        self.root_url = kwargs.pop('root_url', self.ROOT_URL)
        credentials = ('username', 'password', 'api_key',)
        for cred in credentials:
            cred_arg = kwargs.get(cred)
            if not cred_arg:
                raise TypeError("Squwaaaakkk! perchy needs a {} kwarg!".format(cred))
            setattr(self, cred, cred_arg)

    def setup_endpoints(self):
        pass
