import pytest
from django.conf import settings
from django.http import HttpResponse

from django_toolkit import middlewares


class TestVersionHeaderMiddleware(object):

    @pytest.fixture(autouse=True)
    def settings(self, settings):
        settings.TOOLKIT = {
            'API_VERSION': '1.2.3',
        }
        return settings

    @pytest.fixture
    def middleware(self):
        return middlewares.VersionHeaderMiddleware()

    @pytest.fixture
    def http_request(self, rf):
        return rf.get('/')

    @pytest.fixture
    def http_response(self):
        return HttpResponse()

    def test_should_return_a_response(
        self,
        middleware,
        http_request,
        http_response
    ):
        response = middleware.process_response(http_request, http_response)
        assert isinstance(response, HttpResponse)

    def test_should_add_a_version_header_to_the_response(
        self,
        middleware,
        http_request,
        http_response
    ):
        response = middleware.process_response(http_request, http_response)

        assert 'X-API-Version' in response
        assert response['X-API-Version'] == settings.TOOLKIT['API_VERSION']
