import pytest
from unittest import mock

from perch import PerchAPIClient
from perch.endpoints import ENDPOINTS
from perch.main import EndpointCrud


def mock_auth(*args, **kwargs):
    class MockResponse:
        def __init__(self, json_data, status_code):
            self.json_data = json_data
            self.status_code = status_code

        def json(self):
            return self.json_data
    json_res = {
        "access_token": "858598cd-842f-4590-8c06-0f31ee2ee012",
        "expires": 1509065895,
        "refresh_token": "262e42a4-a29a-4473-ab61-c8d4c1285398",
        "token_type": "Bearer"
    }
    return MockResponse(json_res, 200)


#XXX: I don't really need a class here, how can I just use functions outside of class?
class DescribeApiClient(object):
    def it_raises_without_username(self):
        with pytest.raises(TypeError):
            PerchAPIClient(password='password')

    def it_raises_without_password(self):
        with pytest.raises(TypeError):
            PerchAPIClient(username='username')

    @mock.patch('perch.main.requests.post', side_effect=mock_auth)
    def it_formats_auth_payload(self, mocked_auth):
        perch = PerchAPIClient(username='username', password='password')
        payload = perch.auth_payload

        assert payload['username'] == 'username'
        assert payload['password'] == 'password'

    @mock.patch('perch.main.requests.post', side_effect=mock_auth)
    def it_sets_auth_headers(self, mocked_auth):
        perch = PerchAPIClient(username='username', password='password')
        assert perch.headers['Authorization'] == 'Bearer 858598cd-842f-4590-8c06-0f31ee2ee012'

    @mock.patch('perch.main.requests.post', side_effect=mock_auth)
    def it_adds_endpoints(self, mocked_auth):
        perch = PerchAPIClient(username='username', password='password')
        for endpoint in ENDPOINTS:
            assert getattr(perch, endpoint['name']) is not None

    def it_converts_verb_names(self):
        assert EndpointCrud.verb_to_name('POST') == 'create'
        assert EndpointCrud.verb_to_name('GET') == 'get'
        assert EndpointCrud.verb_to_name('PUT') == 'update'
        assert EndpointCrud.verb_to_name('DELETE') == 'delete'

    def it_builds_urls(self):
        class MockAPI:
            root_url = 'http://api.local.perchweb.com'

        mock_endpoint = {
            'name': 'mock',
            'path': '/mock/:id',
            'verbs': ('GET',)
        }

        endpoint_crud = EndpointCrud(MockAPI(), **mock_endpoint)
        assert endpoint_crud.build_url('GET') == 'http://api.local.perchweb.com/mock'
        assert endpoint_crud.build_url('GET', id=3) == 'http://api.local.perchweb.com/mock/3'

    def it_raises_on_invalid_build_url(self):
        class MockAPI:
            root_url = 'http://api.local.perchweb.com'

        mock_endpoint = {
            'name': 'mock',
            'path': '/mock/:id/endpoint',
            'verbs': ('DELETE', 'PUT')
        }

        endpoint_crud = EndpointCrud(MockAPI(), **mock_endpoint)
        with pytest.raises(TypeError):
            endpoint_crud.build_url('DELETE')

